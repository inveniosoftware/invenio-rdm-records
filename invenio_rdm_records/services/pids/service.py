# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM PIDs Service."""

from datetime import datetime

from flask_babelex import lazy_gettext as _
from invenio_db import db
from invenio_drafts_resources.services.records import RecordService
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records_resources.services.errors import PermissionDeniedError
from marshmallow import ValidationError

from .errors import PIDTypeNotSupportedError, ProviderNotSupportedError
from .tasks import register_pid, update_pid


class PIDsService(RecordService):
    """RDM PIDs service."""

    def _get_provider(self, scheme, provider_name=None):
        """Get a provider from config."""
        providers = self.config.pids_providers[scheme]
        if not provider_name:
            provider_name = providers["default"]  # mandatory default
        try:
            provider_cls = providers[provider_name]
            return provider_cls()
        except KeyError:
            raise ProviderNotSupportedError(provider_name, scheme)

    def _validate_pids_schemes(self, pids):
        """Validate the pid schemes are supported by the service.

        This would only fail on the REST API or a misconfigured web UI.
        The marshmallow schema validates that the structure of the data is
        correct. This function validates that the given pids are actually
        supported.
        """
        pids_providers = set(self.config.pids_providers.keys())
        all_pids = set(pids.keys())
        unknown_pids = all_pids - pids_providers
        if unknown_pids:
            raise PIDTypeNotSupportedError(unknown_pids)

    def _validate_pids(self, pids, record, errors):
        """Validate an iterator of PIDs.

        This function assumes all pid types are supported by the system.
        """
        for scheme, pid in pids.items():
            provider_name = pid.get("provider")
            provider = self._get_provider(scheme, provider_name)
            success, val_errors = provider.validate(record=record, **pid)
            if not success:
                errors.append({
                    "field": f"pids.{scheme}",
                    "message": val_errors
                })

    # FIXME: this should be moved to marshmallow level
    # validation happens before to be able to fail before reserving pids
    # it means a double looping but validation should eventually be moved
    # to marshmallow see invenio-rdm-records/issues/796
    def validate(self, identity, pids, record, errors=None):
        """Validate PIDs."""
        errors = [] if errors is None else errors
        self._validate_pids_schemes(pids)
        self._validate_pids(pids, record, errors)

        return pids

    def resolve(self, id_, identity, pid_type):
        """Resolve PID to a record (not draft)."""
        # get the pid object
        # FIXME: Should not use model class but go through provider?
        pid = PersistentIdentifier.get(pid_type=pid_type, pid_value=id_)

        # get related record
        record = self.record_cls.get_record(pid.object_uuid)

        # permissions
        self.require_permission(identity, "read", record=record)

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    def create_by_type(self, id_, identity, pid_type, pid_provider=None):
        """Create a `NEW` PID for a given record."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        # Permissions
        self.require_permission(identity, "pid_create", record=draft)

        if draft.pids.get(pid_type):
            raise ValidationError(
                message=_("A PID already exists for type {pid_type}")
                .format(pid_type=pid_type),
                field_name=f"pids.{pid_type}",
            )
        provider = self._get_provider(pid_type, pid_provider)
        pid = provider.create(draft)
        draft.pids[pid_type] = {
            "identifier": pid.pid_value,
            "provider": provider.name
        }
        if provider.client:
            draft.pids[pid_type]["client"] = provider.client.name

        draft.commit()
        db.session.commit()
        self.indexer.index(draft)

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
        )

    def _create_many(self, draft, pids):
        """Create many PIDs."""
        for scheme, pid in pids.items():
            pid_value = pid.get("identifier")
            provider = self._get_provider(scheme, pid.get("provider"))
            # the pid will be reactivated if it was deleted
            try:
                pid = provider.get(pid_value=pid_value)
            except PIDDoesNotExistError:
                pid = None

            if not pid or pid.is_deleted():
                pid = provider.create(
                    record=draft, value=pid_value, status=PIDStatus.RESERVED
                )

            if provider.client:  # provider and identifier already in dict
                pids[scheme]["client"] = provider.client.name

        return pids

    def create_many(self, id_, identity, pids):
        """Create many PIDs for a given draft.

        This method assumes all pids have a value, otherwise
        use `create_many_by_type`.
        """
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_create", record=draft)

        pids, errors = self.validate(identity, pids, draft)
        if errors:
            raise ValidationError(message=errors)

        draft.pids = self._create_many(draft, pids)

        draft.commit()
        db.session.commit()
        self.indexer.index(draft)

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
            errors=errors
        )

    def _create_required(self, draft):
        """Create the required PIDs."""
        pids = {}
        pid_types = self.config.pids_required
        for scheme in pid_types:
            if not draft.pids.get(scheme):
                # FIXME: should fail if required and external but no value
                provider = self._get_provider(scheme)
                # FIXME: raising here is too ad hoc
                if not provider.is_managed():
                    raise ValidationError(
                        message=_("External identifier value is required."),
                        field_name=f"pids.{scheme}"
                    )
                pid = provider.create(record=draft, status=PIDStatus.RESERVED)
                pid_attrs = {
                    "identifier": pid.pid_value,
                    "provider": provider.name,
                }
                if provider.client:
                    pid_attrs["client"] = provider.client.name
                pids[scheme] = pid_attrs

        return pids

    def create_required(self, id_, identity):
        """Create the required PIDs for a given draft."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_create", record=draft)
        draft.pids = self._create_many_by_type(draft)

        draft.commit()
        db.session.commit()
        self.indexer.index(draft)

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
        )

    def _update(self, identity, draft, pids, errors):
        """Update a list of PIDs based on a draft."""
        updated_pids = dict(draft.get("pids", {}))  # force copy

        for scheme, old_pid in draft.get("pids", {}).items():
            updated_pid = pids.get(scheme)
            if old_pid != updated_pid:
                try:  # record and scheme reach the generator as "over"
                    self.require_permission(
                        identity, 'pid_delete', record=draft, scheme=scheme
                    )

                    # delete if existant in db
                    pid_value = old_pid.get("identifier")
                    if pid_value:  # e.g. remove external and incomplete pid
                        provider = self._get_provider(
                            scheme, old_pid.get("provider")
                        )
                        try:
                            pid = provider.get(pid_value=pid_value)
                            provider.delete(pid, record=draft)
                        except PIDDoesNotExistError:
                            pass  # does not exist, no need to delete it
                    # remove or replace by the new pid
                    updated_pids.pop(scheme, None)
                    if updated_pid:  # an update could be a removal
                        updated_pids[scheme] = updated_pid

                except PermissionDeniedError:
                    errors.append({
                        "field": f"pids.{scheme}",
                        "message": _("Permission denied: cannot update PID.")
                    })
                    continue

        # add new pids to the draft
        new_pids = set(pids.keys()) - set(updated_pids.keys())
        for new_pid in new_pids:
            updated_pids[new_pid] = pids[new_pid]

        return updated_pids

    def update(self, id_, identity, pids):
        """Update draft PIDs."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        # check for creation, deletion is scheme specific
        self.require_permission(identity, "pid_create", record=draft)

        pids, errors = self.validate(identity, pids, draft)
        if errors:
            raise ValidationError(message=errors)

        draft.pids, errors = self._update(identity, draft, pids, errors)

        draft.commit()
        db.session.commit()
        self.indexer.index(draft)

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
            errors=errors
        )

    def update_remote(self, id_, identity, pid_type):
        """Update a registered PID on a remote provider."""
        record = self.record_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_update", record=record)

        pid_attrs = record.pids.get(pid_type, None)

        if not pid_attrs:
            raise ValidationError(
                message=_("PID not found for type {pid_type}")
                .format(pid_type=pid_type),
                field_name=f"pids",
            )

        provider_name = pid_attrs["provider"]
        provider = self._get_provider(pid_type, provider_name)
        pid_value = pid_attrs["identifier"]
        pid = provider.get(pid_value=pid_value, pid_type=pid_type)

        provider.update(pid, record=record)
        db.session.commit()  # no need for record.commit, it does not change

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    def _reserve(self, draft, pids):
        """Reserve PIDs from a list."""
        for scheme, pid in pids.items():
            provider = self._get_provider(scheme, pid["provider"])
            pid = provider.get(pid["identifier"])
            if pid.is_new():  # not reserved and not registered
                provider.reserve(pid, record=draft)

        return True

    def reserve(self, id_, identity):
        """Reserve PIDs of a record."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_manage", record=draft)
        self._reserve(draft, draft.pids)

        # draft and index do not need commit/refresh
        db.session.commit()

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
        )

    # FIXME: This logic should move to the cmp.post_publish
    def register_or_update(self, record, delay=False):
        """Registers or updates PIDs.

        Triggers an asynchronous task.
        """
        pids = record.get('pids', {})

        for scheme, pid_attrs in pids.items():
            provider_name = pid_attrs["provider"]
            identifier_value = pid_attrs["identifier"]
            provider = self._get_provider(scheme, provider_name)
            pid = provider.get(pid_value=identifier_value, pid_type=scheme)
            if delay:
                if pid.is_registered():
                    update_pid.delay(record["id"], pid.pid_type)
                else:
                    register_pid.delay(record["id"], pid.pid_type)
            else:
                if pid.is_registered():
                    update_pid(record["id"], pid.pid_type)
                else:
                    register_pid(record["id"], pid.pid_type)

        return True

    def register_by_type(self, id_, identity, pid_type):
        """Register a PID of a record."""
        record = self.record_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_register", record=record)

        pid_attrs = record.pids.get(pid_type, None)

        if not pid_attrs:
            raise ValidationError(
                message=_("PID not found for type {pid_type}")
                .format(pid_type=pid_type),
                field_name=f"pids",
            )

        provider_name = pid_attrs["provider"]
        provider = self._get_provider(pid_type, provider_name)
        pid_value = pid_attrs["identifier"]
        pid = provider.get(pid_value=pid_value, pid_type=pid_type)

        links = self.links_item_tpl.expand(record)
        provider.register(
            pid, record=record, url=links["self_html"]
        )

        db.session.commit()  # no need for record.commit, it does not change

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    def discard_by_type(self, id_, identity, pid_type, pid_provider=None):
        """Discard a PID for a given draft.

        If the status was `NEW` it will be hard deleted. Otherwise,
        it will be soft deleted (`RESERVED`/`REGISTERED`).
        """
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        # Permissions
        self.require_permission(identity, "pid_discard", record=draft)
        provider = self._get_provider(pid_type, pid_provider)
        try:
            pid_attr = draft.pids[pid_type]
            pid = provider.get_by_record(
                draft.id,
                pid_type=pid_type,
                pid_value=pid_attr["identifier"],
            )
        # KeyError if the pid is not present in the draft
        # PIDDoesNotExistError if not present in DB
        except (KeyError, PIDDoesNotExistError):
            raise ValidationError(
                message=_("No PID found for type {pid_type}")
                .format(pid_type=pid_type),
                field_name=f"pids.{pid_type}",
            )

        provider.delete(pid)
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

    def _discard_all(self, pids):
        """Discard all PIDs."""
        for scheme, pid_attrs in pids.items():
            provider_name = pid_attrs.get("provider")
            provider = self._get_provider(scheme, provider_name)
            try:
                pid = provider.get(pid_value=pid_attrs["identifier"])
                # pids should be status NEW at this point
                if pid.is_new():
                    provider.delete(pid)
            except PIDDoesNotExistError:
                pass  # pid was not saved to pidstore yet, no deletion needed

    def discard_all(self, id_, identity):
        """Discard all PIDs for a given draft.

        If the status was `NEW` it will be hard deleted. Otherwise,
        it will be soft deleted (`RESERVED`/`REGISTERED`).
        """
        # draft_cls because we cannot delete on a published record
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        self.require_permission(identity, "pid_discard", record=draft)

        self._discard_all(draft.get('pids', {}))
        draft.pids = {}

        draft.commit()
        db.session.commit()
        self.indexer.index(draft)

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
        )

    def invalidate(self, *args, **kwargs):
        """Invalidates a registered PID of a Record.

        This operation can only be perfomed by an admin.
        """
        raise NotImplementedError()
