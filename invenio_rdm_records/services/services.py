# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2023 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2021-2023 TU Wien.
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2022 Universität Hamburg.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service."""


import arrow
from invenio_accounts.models import User
from invenio_db import db
from invenio_drafts_resources.services.records import RecordService
from invenio_records_resources.services import LinksTemplate, ServiceSchemaWrapper
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work
from invenio_requests.services.results import EntityResolverExpandableField
from invenio_search.engine import dsl

from invenio_rdm_records.records.models import RDMRecordQuota, RDMUserQuota

from ..records.systemfields.deletion_status import RecordDeletionStatusEnum
from .errors import (
    DeletionStatusException,
    EmbargoNotLiftedError,
    RecordDeletedException,
)
from .results import ParentCommunitiesExpandableField


class RDMRecordService(RecordService):
    """RDM record service."""

    def __init__(
        self,
        config,
        files_service=None,
        draft_files_service=None,
        access_service=None,
        pids_service=None,
        review_service=None,
    ):
        """Constructor for RecordService."""
        super().__init__(config, files_service, draft_files_service)
        self._access = access_service
        self._pids = pids_service
        self._review = review_service

    #
    # Subservices
    #
    @property
    def access(self):
        """Record access service."""
        return self._access

    @property
    def pids(self):
        """Record PIDs service."""
        return self._pids

    @property
    def review(self):
        """Record review service."""
        return self._review

    #
    # Properties
    #
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
    def schema_tombstone(self):
        """Schema for tombstone information."""
        return ServiceSchemaWrapper(self, schema=self.config.schema_tombstone)

    @property
    def schema_quota(self):
        """Returns the featured data schema instance."""
        return ServiceSchemaWrapper(self, schema=self.config.schema_quota)

    #
    # Service methods
    #
    @unit_of_work()
    def lift_embargo(self, identity, _id, uow=None):
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
                uow.register(RecordCommitOp(draft, indexer=self.indexer))

        if not record.access.lift_embargo():
            raise EmbargoNotLiftedError(_id)

        # Commit and reindex record
        uow.register(RecordCommitOp(record, indexer=self.indexer))

    def scan_expired_embargos(self, identity):
        """Scan for records with an expired embargo."""
        today = arrow.utcnow().date().isoformat()

        embargoed_q = (
            f"access.embargo.active:true AND access.embargo.until:[* TO {today}]"
        )

        return self.scan(identity=identity, q=embargoed_q)

    def oai_result_item(self, identity, oai_record_source):
        """Get a result item from a record source in the OAI server.

        This function is ONLY intended to be used by the OAI-PMH server because
        the OAIServer does not use the service directly to retrieve records.
        The OAIServer predates the software architecture and thus to avoid
        rewriting it, we allow exceptions to get data from the search index
        and pass it into the service (normally the service must be responsible
        for this).
        """
        record = self.record_cls.loads(oai_record_source)
        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    #
    # Deletion workflows
    #
    @unit_of_work()
    def delete_record(self, identity, id_, data, expand=False, uow=None):
        """(Soft) delete a published record."""
        record = self.record_cls.pid.resolve(id_)
        if record.deletion_status.is_deleted:
            raise DeletionStatusException(record, RecordDeletionStatusEnum.PUBLISHED)

        # Check permissions
        self.require_permission(identity, "delete", record=record)

        # Load tombstone data with the schema
        data, errors = self.schema_tombstone.load(
            data,
            context={
                "identity": identity,
                "pid": record.pid,
                "record": record,
            },
            raise_errors=True,
        )

        # Run components
        self.run_components(
            "delete_record", identity, data=data, record=record, uow=uow
        )

        # Commit and reindex record
        uow.register(RecordCommitOp(record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def update_tombstone(self, identity, id_, data, expand=False, uow=None):
        """Update the tombstone information for the (soft) deleted record."""
        record = self.record_cls.pid.resolve(id_)
        if not record.deletion_status.is_deleted:
            # strictly speaking, it's two expected statuses: DELETED or MARKED
            raise DeletionStatusException(record, RecordDeletionStatusEnum.DELETED)

        # Check permissions
        self.require_permission(identity, "delete", record=record)

        # Load tombstone data with the schema and set it
        data, errors = self.schema_tombstone.load(
            data,
            context={
                "identity": identity,
                "pid": record.pid,
                "record": record,
            },
            raise_errors=True,
        )

        # Run components
        self.run_components(
            "update_tombstone", identity, data=data, record=record, uow=uow
        )

        # Commit and reindex record
        uow.register(RecordCommitOp(record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def cleanup_record(self, identity, id_, uow=None):
        """Clean up a (soft) deleted record."""
        record = self.record_cls.pid.resolve(id_)
        if not record.deletion_status.is_deleted:
            # strictly speaking, it's two expected statuses: DELETED or MARKED
            raise DeletionStatusException(record, RecordDeletionStatusEnum.DELETED)

        raise NotImplementedError()

    @unit_of_work()
    def restore_record(self, identity, id_, expand=False, uow=None):
        """Restore a record that has been (soft) deleted."""
        record = self.record_cls.pid.resolve(id_)
        if record.deletion_status != RecordDeletionStatusEnum.DELETED:
            raise DeletionStatusException(RecordDeletionStatusEnum.DELETED, record)

        # Check permissions
        self.require_permission(identity, "delete", record=record)

        # Run components
        self.run_components("restore_record", identity, record=record, uow=uow)

        # Commit and reindex record
        uow.register(RecordCommitOp(record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def mark_record_for_purge(self, identity, id_, expand=False, uow=None):
        """Mark a (soft) deleted record for purge."""
        record = self.record_cls.pid.resolve(id_)
        if record.deletion_status != RecordDeletionStatusEnum.DELETED:
            raise DeletionStatusException(record, RecordDeletionStatusEnum.DELETED)

        # Check permissions
        self.require_permission(identity, "purge", record=record)

        # Run components
        self.run_components("mark_record", identity, record=record, uow=uow)

        # Commit and reindex record
        uow.register(RecordCommitOp(record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def unmark_record_for_purge(self, identity, id_, expand=False, uow=None):
        """Remove the mark for deletion from a record, returning it to deleted state."""
        record = self.record_cls.pid.resolve(id_)
        if record.deletion_status != RecordDeletionStatusEnum.MARKED:
            raise DeletionStatusException(record, RecordDeletionStatusEnum.MARKED)

        # Check permissions
        self.require_permission(identity, "purge", record=record)

        # Run components
        self.run_components("unmark_record", identity, record=record, uow=uow)

        # Commit and reindex the record
        uow.register(RecordCommitOp(record, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def purge_record(self, identity, id_, uow=None):
        """Purge a record that has been marked."""
        record = self.record_cls.pid.resolve(id_)
        if record.deletion_status != RecordDeletionStatusEnum.MARKED:
            raise DeletionStatusException(record, RecordDeletionStatusEnum.MARKED)

        raise NotImplementedError()

    #
    # Search functions
    #
    def search(
        self,
        identity,
        params=None,
        search_preference=None,
        expand=False,
        extra_filter=None,
        **kwargs,
    ):
        """Search for published records matching the querystring."""
        return super().search(
            identity,
            params,
            search_preference,
            expand,
            extra_filter=extra_filter,
            permission_action="read_deleted",
            **kwargs,
        )

    def search_drafts(
        self,
        identity,
        params=None,
        search_preference=None,
        expand=False,
        extra_filter=None,
        **kwargs,
    ):
        """Search for drafts that have not been marked as deleted."""
        # because drafts don't have a 'deletion_status', a simple positive filter
        # won't work in cases where records and drafts are mixed...
        published_filter = dsl.Q(
            "term", **{"deletion_status": RecordDeletionStatusEnum.PUBLISHED.value}
        )
        drafts_filter = dsl.Q("term", **{"is_published": False})
        search_filter = drafts_filter | published_filter
        if extra_filter:
            search_filter &= extra_filter
        return super().search_drafts(
            identity,
            params=params,
            search_preference=search_preference,
            expand=expand,
            extra_filter=search_filter,
            **kwargs,
        )

    #
    # Base methods, extended with handling of deleted records
    #
    def read(self, identity, id_, expand=False, include_deleted=False):
        """Retrieve a record."""
        record = self.record_cls.pid.resolve(id_)
        result = super().read(identity, id_, expand=expand)

        if not include_deleted and record.deletion_status.is_deleted:
            raise RecordDeletedException(record, result_item=result)
        if include_deleted and record.deletion_status.is_deleted:
            can_read_deleted = self.check_permission(
                identity, "read_deleted", record=record
            )

            if not can_read_deleted:
                # displays tombstone
                raise RecordDeletedException(record, result_item=result)

        return result

    #
    # Record file quota handling
    #
    def _update_quota(self, record, quota_size, max_file_size, notes):
        """Update record with quota values."""
        record.quota_size = quota_size
        if max_file_size:
            record.max_file_size = max_file_size
        if notes:
            record.notes = notes

    @unit_of_work()
    def set_quota(
        self,
        identity,
        id_,
        data,
        files_attr="files",
        uow=None,
    ):
        """Set draft files quota."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        parent = draft.parent
        self.require_permission(identity, "manage_quota", record=draft)
        data, errors = self.schema_quota.load(
            data,
            context={
                "identity": identity,
            },
            raise_errors=True,
        )
        # Set quota
        draft_quota = RDMRecordQuota.query.filter(
            RDMRecordQuota.parent_id == str(parent.id)
        ).one_or_none()

        if not draft_quota:
            draft_quota = RDMRecordQuota(
                parent_id=str(parent.id),
                user_id=parent.access.owned_by.owner_id,
                **data,
            )
        else:
            # update record quota
            self._update_quota(draft_quota, **data)

        db.session.add(draft_quota)

        # files_attr can be set to "media_files"
        getattr(draft, files_attr).set_quota(
            quota_size=data["quota_size"], max_file_size=data["max_file_size"]
        )
        return True

    #
    #  NOTE this should potentially be moved to users service. Added here for
    # fast tracking its development
    @unit_of_work()
    def set_user_quota(
        self,
        identity,
        id_,
        data,
        uow=None,
    ):
        """Set user files quota."""
        user = User.query.get(id_)

        self.require_permission(identity, "manage_quota", record=user)

        data, errors = self.schema_quota.load(
            data,
            context={
                "identity": identity,
            },
            raise_errors=True,
        )
        # Set quota
        user_quota = RDMUserQuota.query.filter(
            RDMUserQuota.user_id == user.id
        ).one_or_none()
        if not user_quota:
            user_quota = RDMUserQuota(user_id=user.id, **data)
        else:
            # update user quota
            self._update_quota(user_quota, **data)

        db.session.add(user_quota)

        return True
