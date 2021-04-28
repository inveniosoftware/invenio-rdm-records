# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service."""

from datetime import datetime

import arrow
from flask_babelex import lazy_gettext as _
from invenio_db import db
from invenio_drafts_resources.services.records import RecordService
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_resources.services.records.schema import \
    ServiceSchemaWrapper
from marshmallow.exceptions import ValidationError

from ..secret_links.errors import InvalidPermissionLevelError


class RDMRecordService(RecordService):
    """RDM record service."""

    def link_result_item(self, *args, **kwargs):
        """Create a new instance of the resource unit."""
        return self.config.link_result_item_cls(*args, **kwargs)

    def link_result_list(self, *args, **kwargs):
        """Create a new instance of the resource list."""
        return self.config.link_result_list_cls(*args, **kwargs)

    @property
    def schema_secret_link(self):
        """Schema for secret links."""
        return ServiceSchemaWrapper(
            self, schema=self.config.schema_secret_link
        )

    def _validate_secret_link_expires_at(
        self, expires_at, is_specified=True, secret_link=None
    ):
        """Validate the given expiration date.

        If a ``secret_link`` is specified, the validity of setting its
        expiration date to ``expires_at`` will be checked additionally.
        The ``is_specified`` flag hints at if the value of ``expires_at``
        was set in the given data, or if it was omitted (which makes a
        difference in patch operations).
        """
        if expires_at and is_specified:
            # if the expiration date was specified, check if it's in the future
            expires_at = arrow.get(expires_at).to("utc").datetime
            expires_at = expires_at.replace(tzinfo=None)

            if expires_at < datetime.utcnow():
                raise ValidationError(
                    message=_("Expiration date must be set to the future"),
                    field_name="expires_at",
                )

        if secret_link is not None:
            # if we're updating an existing secret link, we need to do some
            # more checks...

            # we interpret explicitly setting 'expires_at = null/None' as
            # removing the expiration date (semantically different from not
            # specifying an 'expires_at' value at all, at least for updates)
            increases_expiration = (
                is_specified and not expires_at and secret_link.expires_at
            ) or (
                expires_at
                and secret_link.expires_at
                and expires_at > secret_link.expires_at
            )

            if increases_expiration:
                # it's not a problem to reduce the validity of a token (*),
                # but increasing its lifespan would require a new signature,
                # and thus a new token
                # (*) in that case, the permission generator will still say
                #     no, even if the signature is still valid
                raise ValidationError(
                    message=_("Cannot postpone expiration of links"),
                    field_name="expires_at",
                )

            elif expires_at and expires_at < datetime.utcnow():
                raise ValidationError(
                    message=_("Expiration date must be set to the future"),
                    field_name="expires_at",
                )

        return expires_at

    def create_secret_link(
        self,
        id_,
        identity,
        data,
        links_config=None,
    ):
        """Create a secret link for a record (resp. its parent)."""
        record, parent = self._get_record_and_parent_by_id(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Validation
        data, __ = self.schema_secret_link.load(
            data, context=dict(identity=identity), raise_errors=True
        )
        expires_at = self._validate_secret_link_expires_at(
            data.get("expires_at")
        )
        if "permission" not in data:
            raise ValidationError(
                _("An access permission level is required"),
                field_name="permission",
            )

        # Creation
        try:
            link = parent.access.links.create(
                permission_level=data["permission"],
                expires_at=expires_at,
                extra_data=data.get("extra_data", {}),
            )
        except InvalidPermissionLevelError:
            raise ValidationError(
                _("Invalid access permission level."),
                field_name="permission",
            )

        # Commit and index
        parent.commit()
        if record:
            record.commit()

        db.session.commit()
        self._index_related_records(record, parent)

        return self.link_result_item(
            self,
            identity,
            link,
            links_config=links_config,
        )

    def read_secret_links(
        self,
        id_,
        identity,
        links_config=None,
    ):
        """Read the secret links of a record (resp. its parent)."""
        record, parent = self._get_record_and_parent_by_id(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Fetching
        links = parent.access.links.resolve_all()
        return self.link_result_list(
            service=self,
            identity=identity,
            results=links,
            links_config=links_config,
        )

    def read_secret_link(
        self,
        id_,
        identity,
        link_id,
        links_config=None,
    ):
        """Read a specific secret link of a record (resp. its parent)."""
        record, parent = self._get_record_and_parent_by_id(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Fetching
        link_ids = [link.link_id for link in parent.access.links]
        if str(link_id) not in link_ids:
            raise LookupError(str(link_id))

        link_idx = link_ids.index(link_id)
        link = parent.access.links[link_idx].resolve()

        return self.link_result_item(
            self,
            identity,
            link,
            links_config=links_config,
        )

    def update_secret_link(
        self,
        id_,
        identity,
        link_id,
        data,
        links_config=None,
    ):
        """Update a secret link for a record (resp. its parent)."""
        record, parent = self._get_record_and_parent_by_id(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Fetching (required for parts of the validation)
        link_ids = [link.link_id for link in parent.access.links]
        if str(link_id) not in link_ids:
            raise LookupError(str(link_id))

        link_idx = link_ids.index(link_id)
        link = parent.access.links[link_idx].resolve()

        # Validation
        data, __ = self.schema_secret_link.load(
            data, context=dict(identity=identity), raise_errors=True
        )
        permission = data.get("permission")
        expires_at = self._validate_secret_link_expires_at(
            data.get("expires_at"),
            is_specified=("expires_at" in data),
            secret_link=link,
        )

        # Update
        # note: we can't update the link's extra data, as that is encoded
        #       in the token and would thus require a new token
        link.expires_at = expires_at or link.expires_at
        link.permission_level = permission or link.permission_level

        # Commit and index
        parent.commit()
        if record:
            record.commit()

        db.session.commit()
        self._index_related_records(record, parent)

        return self.link_result_item(
            self,
            identity,
            link,
            links_config=links_config,
        )

    def delete_secret_link(
        self,
        id_,
        identity,
        link_id,
        links_config=None,
    ):
        """Delete a secret link for a record (resp. its parent)."""
        record, parent = self._get_record_and_parent_by_id(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Fetching
        link_ids = [link.link_id for link in parent.access.links]
        if str(link_id) not in link_ids:
            raise LookupError(str(link_id))

        link_idx = link_ids.index(link_id)
        link = parent.access.links[link_idx].resolve()

        # Deletion
        parent.access.links.pop(link_idx)
        link.revoke()

        # Commit and index
        parent.commit()
        if record:
            record.commit()

        db.session.commit()
        self._index_related_records(record, parent)

        return True

    # PIDS-FIXME: extract to a subservice

    def get_client(self, client_name):
        """Get the provider client from config."""
        client_class = self.config.pids_providers_clients[client_name]
        return client_class(name=client_name)

    def get_managed_provider(self, providers_dict):
        """Get the provider set as system managed."""
        for name, attrs in providers_dict.items():
            if attrs["system_managed"]:
                return name, attrs

    def get_required_provider(self, providers_dict):
        """Get the provider set as required."""
        for name, attrs in providers_dict.items():
            if attrs["required"]:
                return name, attrs

    def get_provider(self, scheme, provider_name=None, client_name=None):
        """Get a provider from config."""
        try:
            providers = self.config.pids_providers[scheme]

            if provider_name:
                provider_config = providers[provider_name]
            else:
                # if no name provided, one of the configured must be required
                _provider = self.get_required_provider(providers)
                if not _provider:
                    # there are no required providers
                    return None
                else:
                    name, provider_config = _provider

            provider_class = provider_config["provider"]
        except ValueError:
            raise ValidationError(
                message=_(f"Unknown PID provider for {scheme}"),
                field_name=f"pids.{scheme}",
            )

        try:
            if client_name:
                client = self.get_client(client_name)
                return provider_class(client)
            elif provider_config["system_managed"]:
                # use as default the client configured for the provider
                provider_name = provider_class.name
                client = self.get_client(provider_name)
                return provider_class(client)

            return provider_class()
        except ValueError:
            raise ValidationError(
                message=_(f"{client_name} not supported for PID {scheme}"),
                ield_name=f"pids.{scheme}",
            )

    def reserve_pid(self, id_, identity, pid_type, pid_client=None):
        """Reserve PID for a given record."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        # Permissions
        self.require_permission(identity, "pid_reserve", record=draft)

        providers = self.config.pids_providers[pid_type]
        _provider = self.get_managed_provider(providers)
        if not _provider:
            raise Exception(f"No managed provider configured for {pid_type}.")

        provider_name, _ = _provider
        provider = self.get_provider(pid_type, provider_name=provider_name,
                                     client_name=pid_client)
        pid = provider.create(draft)

        draft.pids[pid_type] = {
            "identifier": pid.pid_value,
            "provider": provider.name
        }
        if provider.client:
            draft.pids[pid_type]["client"] = provider.client.name

        provider.reserve(pid, draft)
        draft.commit()

        db.session.commit()
        self.indexer.index(draft)

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
        )

    def resolve_pid(self, id_, identity, pid_type):
        """Resolve PID to a record."""
        pid = PersistentIdentifier.get(pid_type=pid_type, pid_value=id_)

        # get related record/draft
        record = self.record_cls.get_record(pid.object_uuid)

        # permissions
        self.require_permission(identity, "read", record=record)

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    def discard_pid(self, id_, identity, pid_type, pid_client=None):
        """Discard a previously reserved PID for a given record.

        It will be soft deleted if already registered.
        """
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        # Permissions
        self.require_permission(identity, "pid_delete", record=draft)

        providers = self.config.pids_providers[pid_type]
        _provider = self.get_managed_provider(providers)
        if not _provider:
            raise Exception(f"No managed provider configured for {pid_type}.")

        provider_name, _ = _provider
        provider = self.get_provider(pid_type, provider_name=provider_name,
                                     client_name=pid_client)
        pid_attr = draft.pids[pid_type]

        try:
            pid = provider.get_by_record(
                draft.id,
                pid_type=pid_type,
                pid_value=pid_attr["identifier"],
            )
        except PIDDoesNotExistError:
            raise ValidationError(
                message=_(f"No registered PID found for type {pid_type}"),
                field_name=f"pids.{pid_type}",
            )

        provider.delete(pid, draft)
        draft.pids.pop(pid_type)
        draft.commit()

        db.session.commit()
        self.indexer.index(draft)

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
        )
