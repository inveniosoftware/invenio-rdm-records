# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2021-2023 TU Wien.
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2022 Universität Hamburg.
# Copyright (C) 2024 KTH Royal Institute of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service."""

from datetime import datetime

import arrow
from flask import current_app
from invenio_access.permissions import system_user_id
from invenio_accounts.models import User
from invenio_db import db
from invenio_drafts_resources.services.records import RecordService
from invenio_drafts_resources.services.records.uow import ParentRecordCommitOp
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services import LinksTemplate, ServiceSchemaWrapper
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    RecordIndexDeleteOp,
    RecordIndexOp,
    TaskOp,
    unit_of_work,
)
from invenio_requests.services.results import EntityResolverExpandableField
from invenio_search.engine import dsl
from marshmallow import ValidationError
from sqlalchemy.exc import NoResultFound

from invenio_rdm_records.records.models import RDMRecordQuota, RDMUserQuota
from invenio_rdm_records.services.pids.tasks import register_or_update_pid

from ..records.systemfields.deletion_status import RecordDeletionStatusEnum
from .errors import (
    CommunityRequiredError,
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
            EntityResolverExpandableField("parent.access.owned_by"),
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

        # Run components
        self.run_components(
            "lift_embargo", identity, draft=draft, record=record, uow=uow
        )

        self._pids.pid_manager.create_and_reserve(record)
        uow.register(RecordCommitOp(record, indexer=self.indexer))
        uow.register(TaskOp(register_or_update_pid, record["id"], "doi", parent=False))
        # If the record was previously public it will still keep the parent PID
        if not record.parent.pids:
            self._pids.parent_pid_manager.create_and_reserve(record.parent)
            uow.register(
                ParentRecordCommitOp(
                    record.parent,
                )
            )
            uow.register(
                TaskOp(register_or_update_pid, record["id"], "doi", parent=True)
            )

    def scan_expired_embargos(self, identity):
        """Scan for records with an expired embargo."""
        today = arrow.utcnow().date().isoformat()

        embargoed_q = (
            f"access.embargo.active:true AND access.embargo.until:[* TO {today}]"
        )

        return self.scan(identity=identity, q=embargoed_q, params={"allversions": True})

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
    def delete_record(
        self, identity, id_, data, expand=False, uow=None, revision_id=None
    ):
        """(Soft) delete a published record."""
        record = self.record_cls.pid.resolve(id_)
        # Check permissions
        self.require_permission(identity, "delete", record=record)

        self.check_revision_id(record, revision_id)

        if record.deletion_status.is_deleted:
            raise DeletionStatusException(record, RecordDeletionStatusEnum.PUBLISHED)

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

        new_record_latest_version = None
        if record.versions.is_latest is True:
            # set latest to the previous non deleted record
            new_record_latest_version = (
                self.record_cls.next_latest_published_record_by_parent(record.parent)
            )
            if new_record_latest_version:
                new_record_latest_version.versions.set_latest()

        # Commit and reindex record
        uow.register(RecordCommitOp(record, indexer=self.indexer))

        # delete associated draft from index
        try:
            draft = self.draft_cls.pid.resolve(id_)
            uow.register(RecordIndexDeleteOp(draft, indexer=self.draft_indexer))
        except NoResultFound:
            pass

        # Commit and reindex new latest record
        if new_record_latest_version:
            uow.register(
                RecordCommitOp(new_record_latest_version, indexer=self.indexer)
            )

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

        # set latest to the previous non deleted record
        latest_record_version = self.record_cls.get_latest_published_by_parent(
            record.parent
        )

        if not latest_record_version:
            # if all records were deleted then make the restored record latest
            record.versions.set_latest()
        elif record.versions.index > latest_record_version.versions.index:
            # set current restored record as latest
            record.versions.set_latest()

        # Commit and reindex record
        uow.register(RecordCommitOp(record, indexer=self.indexer))

        # reindex associated draft
        try:
            draft = self.draft_cls.pid.resolve(id_)
            uow.register(RecordIndexOp(draft, indexer=self.draft_indexer))
        except NoResultFound:
            pass

        # commit and reindex the old latest record
        if latest_record_version and record.id != latest_record_version.id:
            uow.register(RecordCommitOp(latest_record_version, indexer=self.indexer))

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

    @unit_of_work()
    def publish(self, identity, id_, uow=None, expand=False):
        """Publish a draft.

        Check for permissions to publish a draft and then call invenio_drafts_resourcs.services.records.services.publish()
        """
        try:
            draft = self.draft_cls.pid.resolve(id_, registered_only=False)
            self.require_permission(identity, "publish", record=draft)
            # By default, admin/superuser has permission to do everything, so PermissionDeniedError won't be raised for admin in any case
        except PermissionDeniedError as exc:
            # If user doesn't have permission to publish, determine which error to raise, based on config
            community_required = current_app.config["RDM_COMMUNITY_REQUIRED_TO_PUBLISH"]
            is_community_missing = len(draft.parent.communities.ids) < 1
            if community_required and is_community_missing:
                raise CommunityRequiredError()
            else:
                # If the config wasn't enabled, then raise the PermissionDeniedError
                raise exc

        return super().publish(identity, id_, uow=uow, expand=expand)

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
        # ATTENTION: super() applies dsl.Q("term", has_draft=False) & search_filter
        #
        # The "has_draft=False" ensures that we return either:
        # - a record without a draft, or
        # - a draft
        #
        # To filter out deleted records we apply the following logic:
        #   deletion_status=="P" or "deletion_status" not in data
        search_filter = dsl.query.Q(
            "bool",
            should=[
                dsl.query.Q(
                    "bool",
                    must=[
                        dsl.query.Q(
                            "term",
                            deletion_status=RecordDeletionStatusEnum.PUBLISHED.value,
                        )
                    ],
                ),
                # Drafts does not have deletion_status so this clause is needed to
                # prevent the above clause from filtering out the drafts
                # TODO: ensure draft also has the needed data.
                dsl.query.Q(
                    "bool", must_not=[dsl.query.Q("exists", field="deletion_status")]
                ),
            ],
        )
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

    def search_versions(
        self, identity, id_, params=None, search_preference=None, expand=False, **kwargs
    ):
        """Search for published records matching the querystring."""
        return super().search_versions(
            identity,
            id_,
            params,
            search_preference,
            expand,
            permission_action="read_deleted",
            **kwargs,
        )

    def scan_versions(
        self,
        identity,
        id_,
        params=None,
        search_preference=None,
        expand=False,
        permission_action="read_deleted",
        **kwargs,
    ):
        """Search for record's versions."""
        try:
            record = self.record_cls.pid.resolve(id_, registered_only=False)
        except NoResultFound:
            record = self.draft_cls.pid.resolve(id_, registered_only=False)

        self.require_permission(identity, "read", record=record)
        extra_filter = dsl.Q("term", **{"parent.id": str(record.parent.pid.pid_value)})
        if filter_ := kwargs.pop("extra_filter", None):
            extra_filter = filter_ & extra_filter

        # Prepare and execute the search
        params = params or {}

        search_result = self._search(
            "search_versions",
            identity,
            params,
            search_preference,
            record_cls=self.record_cls,
            search_opts=self.config.search_versions,
            extra_filter=extra_filter,
            permission_action=permission_action,
            **kwargs,
        ).scan()
        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_search_versions,
                context={"pid_value": id_, "args": params},
            ),
            links_item_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
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

    def read_draft(self, identity, id_, expand=False):
        """Retrieve a draft of a record.

        If the draft has a "deleted" published record then we return 410.
        """
        result = super().read_draft(identity, id_, expand=expand)
        # check that if there is a published deleted record then return 410
        draft = result._record
        if draft.is_published:
            record = self.record_cls.pid.resolve(id_)
            if record.deletion_status.is_deleted:
                result = super().read(identity, id_, expand=expand)
                raise RecordDeletedException(record, result_item=result)

        return result

    @unit_of_work()
    def update_draft(
        self, identity, id_, data, revision_id=None, uow=None, expand=False
    ):
        """Replace a draft."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        # can not make record restricted after grace period
        current_draft_is_public = (
            draft.get("access", {}).get("record", None) == "public"
        )
        is_update_to_restricted = (
            data.get("access", {}).get("record", None) == "restricted"
        )
        allow_restriction = current_app.config[
            "RDM_RECORDS_ALLOW_RESTRICTION_AFTER_GRACE_PERIOD"
        ]

        if (
            not allow_restriction
            and current_draft_is_public
            and is_update_to_restricted
        ):
            end_of_grace_period = (
                draft.created
                + current_app.config["RDM_RECORDS_RESTRICTION_GRACE_PERIOD"]
            )
            if end_of_grace_period <= datetime.now():
                raise ValidationError(
                    _(
                        "Record visibility can not be changed to restricted "
                        "anymore. Please contact support if you still need to make these changes."
                    )
                )

        return super().update_draft(
            identity,
            id_,
            data,
            revision_id=revision_id,
            uow=uow,
            expand=expand,
        )

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
        if user.id == system_user_id:
            user_quota = None
        else:
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

    def search_revisions(self, identity, id_):
        """Return a list of record revisions."""
        record = self.record_cls.pid.resolve(id_)
        # Check permissions
        self.require_permission(identity, "search_revisions", record=record)
        revisions = list(reversed(record.model.versions.all()))

        return self.config.revision_result_list_cls(
            identity,
            revisions,
        )
