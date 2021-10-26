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

from .tasks import register_pid, update_pid


class PIDsService(RecordService):
    """RDM PIDs service."""

    def __init__(self, config, manager_cls):
        """Constructor for RecordService."""
        super().__init__(config)
        self._manager = manager_cls(self.config.pid_providers)

    def resolve(self, id_, identity, scheme):
        """Resolve PID to a record (not draft)."""
        # get the pid object
        # FIXME: Should not use model class but go through provider?
        pid = PersistentIdentifier.get(pid_type=scheme, pid_value=id_)

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

    def create_by_type(self, id_, identity, scheme, pid_provider=None):
        """Create a `NEW` PID for a given record."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_create", record=draft)

        if draft.pids.get(scheme):
            raise ValidationError(
                message=_("A PID already exists for type {scheme}")
                .format(scheme=scheme),
                field_name=f"pids.{scheme}",
            )

        draft.pids[scheme] = self._manager.create_by_type(
            draft, scheme, pid_provider
        )

        draft.commit()
        db.session.commit()
        self.indexer.index(draft)

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
        )

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

        draft.pids = self._manager.create_many(draft, pids)

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

    def create_required(self, id_, identity):
        """Create the required PIDs for a given draft."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_create", record=draft)
        draft.pids = self.create_many_by_scheme(
            draft, self.config.pids_required
        )

        draft.commit()
        db.session.commit()
        self.indexer.index(draft)

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
        )

    def update(self, id_, identity, pids):
        """Update draft PIDs."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        # check for creation, deletion is scheme specific
        self.require_permission(identity, "pid_create", record=draft)

        pids, errors = self.validate(identity, pids, draft)
        if errors:
            raise ValidationError(message=errors)

        draft.pids, errors = self.manager.update(identity, draft, pids, errors)

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

    def update_remote(self, id_, identity, scheme):
        """Update a registered PID on a remote provider."""
        record = self.record_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_update", record=record)

        pid_attrs = record.pids.get(scheme, None)

        if not pid_attrs:
            raise ValidationError(
                message=_("PID not found for type {scheme}")
                .format(scheme=scheme),
                field_name=f"pids",
            )

        provider_name = pid_attrs["provider"]
        provider = self._get_provider(scheme, provider_name)
        pid_value = pid_attrs["identifier"]
        pid = provider.get(pid_value=pid_value, pid_type=scheme)

        provider.update(pid, record=record)
        db.session.commit()  # no need for record.commit, it does not change

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    def reserve(self, id_, identity):
        """Reserve PIDs of a record."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_manage", record=draft)
        self._manager.reserve_many(draft, draft.pids)

        db.session.commit()  # draft and index do not need commit/refresh

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

    def register_by_scheme(self, id_, identity, scheme):
        """Register a PID of a record."""
        record = self.record_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_register", record=record)
        self._manager.register_by_scheme(record, scheme)

        db.session.commit()  # no need for record.commit, it does not change

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    def discard_by_type(self, id_, identity, scheme, pid_provider=None):
        """Discard a PID for a given draft.

        If the status was `NEW` it will be hard deleted. Otherwise,
        it will be soft deleted (`RESERVED`/`REGISTERED`).
        """
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_discard", record=draft)
        self._manager.discard_by_scheme(draft, scheme, pid_provider)
        draft.pids.pop(scheme)

        draft.commit()
        db.session.commit()
        self.indexer.index(draft)

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
        )

    def discard_all(self, id_, identity):
        """Discard all PIDs for a given draft.

        If the status was `NEW` it will be hard deleted. Otherwise,
        it will be soft deleted (`RESERVED`/`REGISTERED`).
        """
        # draft_cls because we cannot delete on a published record
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_discard", record=draft)
        self._manager.discard_all(draft.get('pids', {}))
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
