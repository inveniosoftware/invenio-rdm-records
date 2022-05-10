# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM PIDs Service."""

from invenio_drafts_resources.services.records import RecordService
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work
from invenio_requests.services.results import EntityResolverExpandableField

from invenio_rdm_records.services.results import \
    ParentCommunitiesExpandableField


class PIDsService(RecordService):
    """RDM PIDs service."""

    def __init__(self, config, manager_cls):
        """Constructor for RecordService."""
        super().__init__(config)
        self.manager_cls = manager_cls

    @property
    def expandable_fields(self):
        """Get expandable fields.

        Expand community field to return community details.
        """
        return [
            EntityResolverExpandableField("parent.review.receiver"),
            ParentCommunitiesExpandableField("parent.communities.default"),
        ]

    @property
    def _manager(self):
        """Transitive manager property.

        This is done to:
        - only access self.config attributes when in an application context
        - limit code change
        - limit side-effects (in case using pre-existing `pid_manager` would
                              cause some.)
        """
        return self.manager_cls(self.config.pids_providers)

    @property
    def pid_manager(self):
        """PID Manager."""
        return self._manager

    def resolve(self, identity, id_, scheme, expand=False):
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
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def create(self, identity, id_, scheme, provider=None, uow=None,
               expand=False):
        """Create a `NEW` PID for a given record."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_create", record=draft)
        draft.pids[scheme] = self._manager.create(
            draft, scheme, provider_name=provider
        )

        uow.register(RecordCommitOp(draft, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def update(self, identity, id_, scheme, uow=None, expand=False):
        """Update a registered PID on a remote provider."""
        record = self.record_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_update", record=record)
        self._manager.update(record, scheme)

        # draft and index do not need commit/refresh

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def reserve(self, identity, id_, uow=None, expand=False):
        """Reserve PIDs of a record."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_manage", record=draft)
        self.pid_manager.validate(draft.pids, draft, raise_errors=True)
        self._manager.reserve_all(draft, draft.pids)

        # draft and index do not need commit/refresh

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def register_or_update(self, identity, id_, scheme, uow=None,
                           expand=False):
        """Register or update a PID of a record.

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
            self._manager.update(record, scheme)
        else:
            self.require_permission(identity, "pid_register", record=record)
            # Determine landing page (use scheme specific if available)
            links = self.links_item_tpl.expand(record)
            url = links['self_html']
            if f'self_{scheme}' in links:
                url = links[f'self_{scheme}']
            self._manager.register(
                record,
                scheme,
                url
            )

        # draft and index do not need commit/refresh

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def discard(self, identity, id_, scheme, provider=None, uow=None,
                expand=False):
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

        uow.register(RecordCommitOp(draft, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    def invalidate(self, *args, **kwargs):
        """Invalidates a registered PID of a Record.

        This operation can only be performed by an admin.
        """
        raise NotImplementedError()
