# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM PIDs Service."""

from invenio_drafts_resources.services.records import RecordService
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_resources.services.errors import (
    PermissionDeniedError,
    RecordPermissionDeniedError,
)
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work
from invenio_requests.services.results import EntityResolverExpandableField
from sqlalchemy.orm.exc import NoResultFound

from ...utils import ChainObject
from ..results import ParentCommunitiesExpandableField


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
            EntityResolverExpandableField("parent.access.owned_by"),
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
        return self.manager_cls(self.config.pids_providers, self.config.pids_required)

    @property
    def pid_manager(self):
        """PID Manager."""
        return self._manager

    @property
    def parent_pid_manager(self):
        """Parent PID Manager."""
        return self.manager_cls(
            self.config.parent_pids_providers, self.config.parent_pids_required
        )

    def resolve(self, identity, id_, scheme, expand=False):
        """Resolve PID to a record (not draft)."""
        # FIXME: Should not use model class but go through provider?
        pid = PersistentIdentifier.get(pid_type=scheme, pid_value=id_)
        record = None
        try:
            record = self.record_cls.get_record(pid.object_uuid)
        except NoResultFound:
            # Try to fetch the latest record version
            try:
                version_state = self.record_cls.versions.resolve(
                    parent_id=pid.object_uuid
                )
                if version_state and version_state.latest_id:
                    record = self.record_cls.get_record(version_state.latest_id)
            except NoResultFound:
                pass

        if record is None:
            raise PIDDoesNotExistError(scheme, id_)

        try:
            self.require_permission(identity, "read", record=record)
        except PermissionDeniedError:
            raise RecordPermissionDeniedError(action_name="read", record=record)

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def create(self, identity, id_, scheme, provider=None, uow=None, expand=False):
        """Create a `NEW` PID for a given record."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_create", record=draft)
        draft.pids[scheme] = self._manager.create(draft, scheme, provider_name=provider)

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
    def register_or_update(
        self,
        identity,
        id_,
        scheme,
        parent=False,
        uow=None,
        expand=False,
    ):
        """Register or update a PID of a record.

        If the PID has already been register it updates the remote.
        """
        record = self.record_cls.pid.resolve(id_, registered_only=False)

        if parent:
            # We need the latest record version for the metadata of the parent
            if not record.versions.is_latest:
                record = self.record_cls.get_record(record.versions.latest_id)
            # We're "extending" the attribute and index lookup of the parent
            # to fallback to the record (e.g. for accessing `record.metadata`
            # in the serializer).
            pid_record = ChainObject(
                record.parent,
                record,
                aliases={
                    "_parent": record.parent,
                    "_child": record,
                },
            )
            pid_manager = self.parent_pid_manager
        else:
            pid_record = record
            pid_manager = self.pid_manager

        # no need to validate since the record class was already published
        pid_attrs = pid_record.pids.get(scheme)
        pid = pid_manager.read(scheme, pid_attrs["identifier"], pid_attrs["provider"])

        # Determine landing page (use scheme specific if available)
        links = self.links_item_tpl.expand(identity, record)
        link_prefix = "parent" if parent else "self"
        link_choices = [
            f"{link_prefix}_{scheme}_html",
            f"{link_prefix}_html",
        ]
        for link_id in link_choices:
            if link_id in links:
                url = links[link_id]
                break

        # NOTE: This is not the best place to do this, since we shouldn't be aware of
        #       the fact that the record has a `RelationsField``. However, without
        #       dereferencing, we're not able to serialize the record properly for
        #       registration/updates (e.g. for the DataCite DOIs).
        #       Some possible alternatives:
        #
        #       - Fetch the record from the service, so that it is already in a
        #         serializable dereferenced state.
        #       - Bake-in the dereferencing in the serializer, though this would
        #         be not very consistent regarding the architecture layers.
        relations = getattr(pid_record, "relations", None)
        if relations:
            relations.dereference()

        if pid.is_registered():
            self.require_permission(identity, "pid_update", record=record)
            pid_manager.update(pid_record, scheme, url=url)
        else:
            self.require_permission(identity, "pid_register", record=record)
            pid_manager.register(pid_record, scheme, url=url)

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
    def discard(self, identity, id_, scheme, provider=None, uow=None, expand=False):
        """Discard a PID for a given draft.

        If the status was `NEW` it will be hard deleted. Otherwise,
        it will be soft deleted (`RESERVED`/`REGISTERED`).
        """
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "pid_discard", record=draft, scheme=scheme)
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
