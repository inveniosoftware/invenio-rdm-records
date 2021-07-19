# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service."""

import arrow
from flask_babelex import lazy_gettext as _
from invenio_db import db
from invenio_drafts_resources.services.records import RecordService
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from marshmallow.exceptions import ValidationError

from invenio_rdm_records.services.errors import EmbargoNotLiftedError


class RDMRecordService(RecordService):
    """RDM record service."""

    def __init__(self, config, files_service=None, draft_files_service=None,
                 secret_links_service=None):
        """Constructor for RecordService."""
        super().__init__(config, files_service, draft_files_service)
        self._secret_links = secret_links_service

    #
    # Subservice
    #
    @property
    def secret_links(self):
        """Record secret link service."""
        return self._secret_links

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
                message=_("Unknown PID provider for {scheme}").format(
                    scheme=scheme),
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
                message=_("{client_name} not supported for PID {scheme}")
                .format(client_name=client_name, scheme=scheme),
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
                message=_("No registered PID found for type {pid_type}")
                .format(pid_type=pid_type),
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

    def lift_embargo(self, _id, identity):
        """Lifts embargo from the record and draft (if exists).

        It's an error if you try to lift an embargo that has not yet expired.
        Use this method in combination with scan_expired_embargos().
        """
        # Get the record
        record = self.record_cls.pid.resolve(_id)

        # Check permissions
        self.require_permission(identity, "lift_embargo", record=record)

        # Modify draft embargo if draft exists and it's the same as the record.
        draft = None
        if record.has_draft:
            draft = self.draft_cls.pid.resolve(_id, registered_only=False)
            if record.access == draft.access:
                if not draft.access.lift_embargo():
                    raise EmbargoNotLiftedError(_id)
                draft.commit()

        if not record.access.lift_embargo():
            raise EmbargoNotLiftedError(_id)
        record.commit()

        db.session.commit()
        self.indexer.index(record)
        if draft:
            self.indexer.index(draft)

    def scan_expired_embargos(self, identity):
        """Scan for records with an expired embargo."""
        today = arrow.utcnow().date().isoformat()

        embargoed_q = \
            f"access.embargo.active:true " \
            f"AND access.embargo.until:[* TO {today}]"

        return self.scan(identity=identity, q=embargoed_q)
