# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM PIDs Service."""

from flask_babelex import lazy_gettext as _
from invenio_db import db
from invenio_drafts_resources.services.records import RecordService
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_resources.services.errors import PermissionDeniedError


class PIDsService(RecordService):
    """RDM PIDs service."""

    def __init__(self, config, manager_cls):
        """Constructor for RecordService."""
        super().__init__(config)
        self._manager = manager_cls(self.config.pids_providers)

    @property
    def pid_manager(self):
        """PID Manager."""
        return self._manager

    def resolve(self, id_, identity, scheme):
        """Resolve PID to a record (not draft)."""
        # FIXME: Should not use model class but go through provider?
        pid = PersistentIdentifier.get(pid_type=scheme, pid_value=id_)
        record = self.record_cls.get_record(pid.object_uuid)
        self.require_permission(identity, "read", record=record)

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    def create(self, id_, identity, scheme, provider=None):
        """Create a `NEW` PID for a given record."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_create", record=draft)
        draft.pids[scheme] = self._manager.create(
            draft, scheme, provider_name=provider
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

    def update_remote(self, id_, identity, scheme):
        """Update a registered PID on a remote provider."""
        record = self.record_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_update", record=record)
        self._manager.update_remote(record, scheme)

        db.session.commit()  # draft and index do not need commit/refresh

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
        self.pid_manager.validate(draft.pids, draft, raise_errors=True)
        self._manager.reserve_all(draft, draft.pids)

        db.session.commit()  # draft and index do not need commit/refresh

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
        )

    def register(self, id_, identity, scheme):
        """Register a PID of a record."""
        record = self.record_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_register", record=record)
        # no need to validate since the record class was already published
        self._manager.register(
            record, scheme, url=self.links_item_tpl.expand(record)["self_html"]
        )

        db.session.commit()  # draft and index do not need commit/refresh

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    def register_or_update(self, id_, identity, scheme):
        """Register a PID of a record or update.

        If the PID has already been register it updates the remote.
        """
        record = self.record_cls.pid.resolve(id_, registered_only=False)
        # no need to validate since the record class was already published
        pid_attrs = record.pids.get(scheme)
        pid = self._manager.read(
            scheme, pid_attrs["identifier"], pid_attrs["provider"]
        )
        if pid.is_registered():
            self.require_permission(identity, "pid_update", record=record)
            self._manager.update_remote(record, scheme)
        else:
            self.require_permission(identity, "pid_register", record=record)
            self._manager.register(
                record,
                scheme,
                url=self.links_item_tpl.expand(record)["self_html"]
            )

        db.session.commit()  # draft and index do not need commit/refresh

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    def discard(self, id_, identity, scheme, provider=None):
        """Discard a PID for a given draft.

        If the status was `NEW` it will be hard deleted. Otherwise,
        it will be soft deleted (`RESERVED`/`REGISTERED`).
        """
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(
            identity, "pid_discard", record=draft, scheme=scheme
        )
        self.pid_manager.validate(draft.pids, draft, raise_errors=True)
        identifier = draft.pids.get(scheme, {}).get("identifier")
        self._manager.discard(scheme, identifier, provider)
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

    def invalidate(self, *args, **kwargs):
        """Invalidates a registered PID of a Record.

        This operation can only be perfomed by an admin.
        """
        raise NotImplementedError()
