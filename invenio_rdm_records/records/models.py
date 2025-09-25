# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2026 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record and draft database models."""

import uuid
from datetime import datetime, timezone

from invenio_accounts.models import User
from invenio_communities.records.records.models import CommunityRelationMixin
from invenio_db import db
from invenio_drafts_resources.records import (
    DraftMetadataBase,
    ParentRecordMixin,
    ParentRecordStateMixin,
)
from invenio_files_rest.models import Bucket
from invenio_records.models import RecordMetadataBase
from invenio_records_resources.records import FileRecordModelMixin
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils.types import ChoiceType, UUIDType

from .systemfields.deletion_status import RecordDeletionStatusEnum


#
# Parent
#
class RDMParentMetadata(db.Model, RecordMetadataBase):
    """Metadata store for the parent record."""

    __tablename__ = "rdm_parents_metadata"


class RDMParentCommunity(db.Model, CommunityRelationMixin):
    """Relationship between parent record and communities."""

    __tablename__ = "rdm_parents_community"
    __record_model__ = RDMParentMetadata


#
# Records
#
class RDMRecordMetadata(db.Model, RecordMetadataBase, ParentRecordMixin):
    """Represent a bibliographic record metadata."""

    __tablename__ = "rdm_records_metadata"
    __parent_record_model__ = RDMParentMetadata

    # Enable versioning
    __versioned__ = {}

    bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id), index=True)
    bucket = db.relationship(Bucket, foreign_keys=[bucket_id])

    media_bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id), index=True)
    media_bucket = db.relationship(Bucket, foreign_keys=[media_bucket_id])

    # The deletion status is stored in the model so that we can use it in SQL queries
    deletion_status = db.Column(
        ChoiceType(RecordDeletionStatusEnum, impl=db.String(1)),
        nullable=False,
        default=RecordDeletionStatusEnum.PUBLISHED.value,
    )


class RDMFileRecordMetadata(db.Model, RecordMetadataBase, FileRecordModelMixin):
    """File associated with a record."""

    __record_model_cls__ = RDMRecordMetadata

    __tablename__ = "rdm_records_files"

    # Enable versioning
    __versioned__ = {}


class RDMMediaFileRecordMetadata(db.Model, RecordMetadataBase, FileRecordModelMixin):
    """File associated with a record."""

    __record_model_cls__ = RDMRecordMetadata

    __tablename__ = "rdm_records_media_files"

    # Enable versioning
    __versioned__ = {}


#
# Drafts
#
class RDMDraftMetadata(db.Model, DraftMetadataBase, ParentRecordMixin):
    """Draft metadata for a record."""

    __tablename__ = "rdm_drafts_metadata"
    __parent_record_model__ = RDMParentMetadata

    bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id), index=True)
    bucket = db.relationship(Bucket, foreign_keys=[bucket_id])

    media_bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id), index=True)
    media_bucket = db.relationship(Bucket, foreign_keys=[media_bucket_id])


class RDMFileDraftMetadata(db.Model, RecordMetadataBase, FileRecordModelMixin):
    """File associated with a draft."""

    __record_model_cls__ = RDMDraftMetadata

    __tablename__ = "rdm_drafts_files"


class RDMMediaFileDraftMetadata(db.Model, RecordMetadataBase, FileRecordModelMixin):
    """File associated with a draft."""

    __record_model_cls__ = RDMDraftMetadata

    __tablename__ = "rdm_drafts_media_files"


#
# Versions state
#
class RDMVersionsState(db.Model, ParentRecordStateMixin):
    """Store for the version state of the parent record."""

    __tablename__ = "rdm_versions_state"

    __parent_record_model__ = RDMParentMetadata
    __record_model__ = RDMRecordMetadata
    __draft_model__ = RDMDraftMetadata


### RDM record and user quota table


def default_max_file_size(context):
    """Default max_file_size column value."""
    return context.get_current_parameters()["quota_size"]


class RDMRecordQuota(db.Model, db.Timestamp):
    """Store for the files bucket quota for all versions of a record."""

    __tablename__ = "rdm_records_quota"

    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    """Secret link ID."""

    @declared_attr
    def parent_id(cls):
        """Parent record identifier."""
        return db.Column(
            UUIDType,
            # 1) If the parent record is deleted, we automatically delete
            # the parent record quota as well via database-level on delete trigger.
            db.ForeignKey(
                RDMVersionsState.__parent_record_model__.id,
                ondelete="CASCADE",
            ),
            unique=True,
        )

    """Parent record id."""

    user_id = db.Column(db.Integer)
    """User associated with the parent record via parent.access.owned_by.

    This can be useful for e.g. quickly finding all per-record quota increases
    for a certain user (instead of having to query for all of the user's records
    and then finding the quota increases by their parent IDs).
    """

    quota_size = db.Column(
        db.BigInteger,
        nullable=False,
    )
    """Total quota size of the record's bucket."""

    # set to max total size if not there
    max_file_size = db.Column(
        db.BigInteger, nullable=False, default=default_max_file_size
    )
    """Max size of a single file in the record's bucket."""

    notes = db.Column(db.Text, nullable=False, default="")
    """Notes related to setting the quota."""


class RDMUserQuota(db.Model, db.Timestamp):
    """Store for the files bucket quota for a user."""

    __tablename__ = "rdm_users_quota"

    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    """Secret link ID."""

    @declared_attr
    def user_id(cls):
        """Parent record identifier."""
        return db.Column(
            db.Integer,
            # 1) If the parent record is deleted, we automatically delete
            # the parent record quota as well via database-level on delete trigger.
            db.ForeignKey(
                User.id,
                ondelete="CASCADE",
            ),
            unique=True,
        )

    """User id."""

    quota_size = db.Column(
        db.BigInteger,
        nullable=False,
    )
    """Total quota size of the record's bucket."""

    # set to max total size if not there
    max_file_size = db.Column(
        db.BigInteger, nullable=False, default=default_max_file_size
    )
    """Max size of a single file in the record's bucket."""

    notes = db.Column(db.Text, nullable=False, default="")
    """Notes related to setting the quota."""
