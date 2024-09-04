# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2021-2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record and Draft API."""

from flask import current_app, g
from invenio_communities.records.records.systemfields import CommunitiesField
from invenio_db import db
from invenio_drafts_resources.records import Draft, Record
from invenio_drafts_resources.records.api import ParentRecord as ParentRecordBase
from invenio_drafts_resources.services.records.components.media_files import (
    MediaFilesAttrConfig,
)
from invenio_pidstore.models import PIDStatus
from invenio_records.dumpers import SearchDumper
from invenio_records.dumpers.relations import RelationDumperExt
from invenio_records.systemfields import ConstantField, DictField, ModelField
from invenio_records.systemfields.relations import MultiRelationsField
from invenio_records_resources.records.api import FileRecord
from invenio_records_resources.records.dumpers import CustomFieldsDumperExt
from invenio_records_resources.records.systemfields import (
    FilesField,
    IndexField,
    PIDListRelation,
    PIDNestedListRelation,
    PIDRelation,
    PIDStatusCheckField,
)
from invenio_requests.records.api import Request
from invenio_requests.records.dumpers import CalculatedFieldDumperExt
from invenio_requests.records.systemfields.relatedrecord import RelatedRecord
from invenio_vocabularies.contrib.affiliations.api import Affiliation
from invenio_vocabularies.contrib.awards.api import Award
from invenio_vocabularies.contrib.funders.api import Funder
from invenio_vocabularies.contrib.subjects.api import Subject
from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.systemfields.relations import CustomFieldsRelation

from invenio_rdm_records.records.systemfields.deletion_status import (
    RecordDeletionStatusEnum,
)

from . import models
from .dumpers import (
    CombinedSubjectsDumperExt,
    EDTFDumperExt,
    EDTFListDumperExt,
    GrantTokensDumperExt,
    StatisticsDumperExt,
)
from .systemfields import (
    HasDraftCheckField,
    IsVerifiedField,
    ParentRecordAccessField,
    RecordAccessField,
    RecordDeletionStatusField,
    RecordStatisticsField,
    TombstoneField,
)
from .systemfields.access.protection import Visibility
from .systemfields.draft_status import DraftStatus


#
# Parent record API
#
class RDMParent(ParentRecordBase):
    """Example parent record."""

    # Configuration
    model_cls = models.RDMParentMetadata

    dumper = SearchDumper(
        extensions=[
            GrantTokensDumperExt("access.grant_tokens"),
            CalculatedFieldDumperExt("is_verified"),
        ]
    )

    # System fields
    schema = ConstantField("$schema", "local://records/parent-v3.0.0.json")

    access = ParentRecordAccessField()

    review = RelatedRecord(
        Request,
        keys=["type", "receiver", "status"],
    )

    communities = CommunitiesField(models.RDMParentCommunity)

    permission_flags = DictField("permission_flags")

    pids = DictField("pids")

    is_verified = IsVerifiedField("is_verified")


#
# Common properties between records and drafts.
#
class CommonFieldsMixin:
    """Common system fields between records and drafts."""

    versions_model_cls = models.RDMVersionsState
    parent_record_cls = RDMParent

    # Remember to update INDEXER_DEFAULT_INDEX in Invenio-App-RDM if you
    # update the JSONSchema and mappings to a new version.
    schema = ConstantField("$schema", "local://records/record-v6.0.0.json")

    dumper = SearchDumper(
        extensions=[
            EDTFDumperExt("metadata.publication_date"),
            EDTFListDumperExt("metadata.dates", "date"),
            RelationDumperExt("relations"),
            CombinedSubjectsDumperExt(),
            CustomFieldsDumperExt(fields_var="RDM_CUSTOM_FIELDS"),
            StatisticsDumperExt("stats"),
        ]
    )

    relations = MultiRelationsField(
        creator_affiliations=PIDNestedListRelation(
            "metadata.creators",
            relation_field="affiliations",
            keys=["name", "identifiers"],
            pid_field=Affiliation.pid,
            cache_key="affiliations",
        ),
        contributor_affiliations=PIDNestedListRelation(
            "metadata.contributors",
            relation_field="affiliations",
            keys=["name", "identifiers"],
            pid_field=Affiliation.pid,
            cache_key="affiliations",
        ),
        funding_funder=PIDListRelation(
            "metadata.funding",
            relation_field="funder",
            keys=["name", "identifiers"],
            pid_field=Funder.pid,
            cache_key="funders",
        ),
        funding_award=PIDListRelation(
            "metadata.funding",
            relation_field="award",
            keys=["title", "number", "identifiers", "acronym", "program"],
            pid_field=Award.pid,
            cache_key="awards",
        ),
        languages=PIDListRelation(
            "metadata.languages",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("languages"),
            cache_key="languages",
        ),
        resource_type=PIDRelation(
            "metadata.resource_type",
            keys=["title", "props.type", "props.subtype"],
            pid_field=Vocabulary.pid.with_type_ctx("resourcetypes"),
            cache_key="resource_type",
            value_check=dict(tags=["depositable"]),
        ),
        subjects=PIDListRelation(
            "metadata.subjects",
            keys=["subject", "scheme"],
            pid_field=Subject.pid,
            cache_key="subjects",
        ),
        licenses=PIDListRelation(
            "metadata.rights",
            keys=["title", "description", "icon", "props.url", "props.scheme"],
            pid_field=Vocabulary.pid.with_type_ctx("licenses"),
            cache_key="licenses",
        ),
        related_identifiers=PIDListRelation(
            "metadata.related_identifiers",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("resourcetypes"),
            cache_key="resource_type",
            relation_field="resource_type",
            value_check=dict(tags=["linkable"]),
        ),
        title_types=PIDListRelation(
            "metadata.additional_titles",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("titletypes"),
            cache_key="title_type",
            relation_field="type",
        ),
        title_languages=PIDListRelation(
            "metadata.additional_titles",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("languages"),
            cache_key="languages",
            relation_field="lang",
        ),
        creators_role=PIDListRelation(
            "metadata.creators",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("creatorsroles"),
            cache_key="role",
            relation_field="role",
        ),
        contributors_role=PIDListRelation(
            "metadata.contributors",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("contributorsroles"),
            cache_key="role",
            relation_field="role",
        ),
        description_type=PIDListRelation(
            "metadata.additional_descriptions",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("descriptiontypes"),
            cache_key="description_type",
            relation_field="type",
        ),
        description_languages=PIDListRelation(
            "metadata.additional_descriptions",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("languages"),
            cache_key="languages",
            relation_field="lang",
        ),
        date_types=PIDListRelation(
            "metadata.dates",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("datetypes"),
            cache_key="date_types",
            relation_field="type",
        ),
        relation_types=PIDListRelation(
            "metadata.related_identifiers",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("relationtypes"),
            cache_key="relation_types",
            relation_field="relation_type",
        ),
        removal_reason=PIDRelation(
            "tombstone.removal_reason",
            keys=["title"],
            pid_field=Vocabulary.pid.with_type_ctx("removalreasons"),
            cache_key="removal_reason",
        ),
        custom=CustomFieldsRelation("RDM_CUSTOM_FIELDS"),
    )

    bucket_id = ModelField(dump=False)

    bucket = ModelField(dump=False)

    media_bucket_id = ModelField(dump=False)

    media_bucket = ModelField(dump=False)

    access = RecordAccessField()

    is_published = PIDStatusCheckField(status=PIDStatus.REGISTERED, dump=True)

    pids = DictField("pids")

    #: Custom fields system field.
    custom_fields = DictField(clear_none=True, create_if_missing=True)


#
# Draft API
#
class RDMFileDraft(FileRecord):
    """File associated with a draft."""

    model_cls = models.RDMFileDraftMetadata
    record_cls = None  # defined below


class RDMMediaFileDraft(FileRecord):
    """File associated with a draft."""

    model_cls = models.RDMMediaFileDraftMetadata
    record_cls = None  # defined below

    # Stores record files processor information
    processor = DictField(clear_none=True, create_if_missing=True)


def get_files_quota(record=None):
    """Called by the file manager in create_bucket() during record.post_create.

    The quota is checked against the following order:
    - If record is passed, then
        - record.parent quota is checked
        - record.owner quota is cheched
        - default quota
    - If record is not passed e.g new draft then
        - current identity quota is checked
        - default quota
    :returns: dict i.e {quota_size, max_file_size}: dict is passed to the
        Bucket.create(...) method.
    """
    if record is not None:
        assert getattr(record, "parent", None)
        # Check record quota
        record_quota = models.RDMRecordQuota.query.filter(
            models.RDMRecordQuota.parent_id == record.parent.id
        ).one_or_none()
        if record_quota is not None:
            return dict(
                quota_size=record_quota.quota_size,
                max_file_size=record_quota.max_file_size,
            )
        # Next user quota
        user_quota = models.RDMUserQuota.query.filter(
            models.RDMUserQuota.user_id == record.parent.access.owned_by.owner_id
        ).one_or_none()
        if user_quota is not None:
            return dict(
                quota_size=user_quota.quota_size,
                max_file_size=user_quota.max_file_size,
            )
    else:
        # check current user quota
        user_quota = models.RDMUserQuota.query.filter(
            models.RDMUserQuota.user_id == g.identity.id
        ).one_or_none()
        if user_quota is not None:
            return dict(
                quota_size=user_quota.quota_size,
                max_file_size=user_quota.max_file_size,
            )

    # the config variables if not set are mapped to FILES_REST_DEFAULT_QUOTA_SIZE,
    # FILES_REST_DEFAULT_MAX_FILE_SIZE respectively
    return dict(
        quota_size=current_app.config.get("RDM_FILES_DEFAULT_QUOTA_SIZE")
        or current_app.config.get("FILES_REST_DEFAULT_QUOTA_SIZE"),
        max_file_size=current_app.config.get("RDM_FILES_DEFAULT_MAX_FILE_SIZE")
        or current_app.config.get("FILES_REST_DEFAULT_MAX_FILE_SIZE"),
    )


# Alias to get the quota of files for backward compatibility
get_quota = get_files_quota


def get_media_files_quota(record=None):
    """Called by the file manager in create_bucket() during record.post_create.

    The quota is configured using config variables.
        :returns: dict i.e {quota_size, max_file_size}: dict is passed to the
        Bucket.create(...) method.
    """
    return dict(
        quota_size=current_app.config.get("RDM_MEDIA_FILES_DEFAULT_QUOTA_SIZE"),
        max_file_size=current_app.config.get("RDM_MEDIA_FILES_DEFAULT_MAX_FILE_SIZE"),
    )


class RDMDraft(CommonFieldsMixin, Draft):
    """RDM draft API."""

    model_cls = models.RDMDraftMetadata

    index = IndexField("rdmrecords-drafts-draft-v6.0.0", search_alias="rdmrecords")

    files = FilesField(
        store=False,
        dump=False,
        file_cls=RDMFileDraft,
        # Don't delete, we'll manage in the service
        delete=False,
        bucket_args=get_files_quota,
    )

    media_files = FilesField(
        key=MediaFilesAttrConfig["_files_attr_key"],
        bucket_id_attr=MediaFilesAttrConfig["_files_bucket_id_attr_key"],
        bucket_attr=MediaFilesAttrConfig["_files_bucket_attr_key"],
        bucket_args=get_media_files_quota,
        store=False,
        dump=False,
        file_cls=RDMMediaFileDraft,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    has_draft = HasDraftCheckField()

    status = DraftStatus()


RDMFileDraft.record_cls = RDMDraft


class RDMDraftMediaFiles(RDMDraft):
    """RDM Draft media file API."""

    files = FilesField(
        key=MediaFilesAttrConfig["_files_attr_key"],
        bucket_id_attr=MediaFilesAttrConfig["_files_bucket_id_attr_key"],
        bucket_attr=MediaFilesAttrConfig["_files_bucket_attr_key"],
        bucket_args=get_media_files_quota,
        store=False,
        dump=False,
        file_cls=RDMMediaFileDraft,
        # Don't delete, we'll manage in the service
        delete=False,
    )


RDMMediaFileDraft.record_cls = RDMDraftMediaFiles


# Record API
#
class RDMFileRecord(FileRecord):
    """Example record file API."""

    model_cls = models.RDMFileRecordMetadata
    record_cls = None  # defined below


class RDMMediaFileRecord(FileRecord):
    """Example record file API."""

    model_cls = models.RDMMediaFileRecordMetadata
    record_cls = None  # defined below

    # Stores record files processor information
    processor = DictField(clear_none=True, create_if_missing=True)


class RDMRecord(CommonFieldsMixin, Record):
    """RDM Record API."""

    model_cls = models.RDMRecordMetadata

    index = IndexField(
        "rdmrecords-records-record-v7.0.0", search_alias="rdmrecords-records"
    )

    files = FilesField(
        store=False,
        dump=True,
        # Don't dump files if record is public and files restricted.
        dump_entries=lambda record: not (
            record.access.protection.record == Visibility.PUBLIC.value
            and record.access.protection.files == Visibility.RESTRICTED.value
        ),
        file_cls=RDMFileRecord,
        # Don't create
        create=False,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    media_files = FilesField(
        key=MediaFilesAttrConfig["_files_attr_key"],
        bucket_id_attr=MediaFilesAttrConfig["_files_bucket_id_attr_key"],
        bucket_attr=MediaFilesAttrConfig["_files_bucket_attr_key"],
        store=False,
        dump=False,
        file_cls=RDMMediaFileRecord,
        # Don't create
        create=False,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    has_draft = HasDraftCheckField(RDMDraft)

    status = DraftStatus()

    stats = RecordStatisticsField()

    deletion_status = RecordDeletionStatusField()

    tombstone = TombstoneField()

    @classmethod
    def next_latest_published_record_by_parent(cls, parent):
        """Get the next latest published record.

        This method gives back the next published latest record by parent or None if all
        records are deleted i.e `record.deletion_status != 'P'`.

        :param parent: parent record.
        :param excluded_latest: latest record to exclude find next published version
        """
        with db.session.no_autoflush:
            rec_model_query = (
                cls.model_cls.query.filter_by(parent_id=parent.id)
                .filter(
                    cls.model_cls.deletion_status
                    == RecordDeletionStatusEnum.PUBLISHED.value
                )
                .order_by(cls.model_cls.index.desc())
            )
            current_latest_id = cls.get_latest_by_parent(parent, id_only=True)
            if current_latest_id:
                rec_model_query.filter(cls.model_cls.id != current_latest_id)

            rec_model = rec_model_query.first()
            return (
                cls(rec_model.data, model=rec_model, parent=parent)
                if rec_model
                else None
            )

    @classmethod
    def get_latest_published_by_parent(cls, parent):
        """Get the latest published record for the specified parent record.

        It might return None if there is no latest published version i.e not
        published yet or all versions are deleted.
        """
        latest_record = cls.get_latest_by_parent(parent)
        if latest_record.deletion_status != RecordDeletionStatusEnum.PUBLISHED.value:
            return None
        return latest_record


RDMFileRecord.record_cls = RDMRecord


class RDMRecordMediaFiles(RDMRecord):
    """RDM Media file record API."""

    files = FilesField(
        key=MediaFilesAttrConfig["_files_attr_key"],
        bucket_id_attr=MediaFilesAttrConfig["_files_bucket_id_attr_key"],
        bucket_attr=MediaFilesAttrConfig["_files_bucket_attr_key"],
        bucket_args=get_media_files_quota,
        store=False,
        dump=False,
        file_cls=RDMMediaFileRecord,
        # Don't create
        create=False,
        # Don't delete, we'll manage in the service
        delete=False,
    )


RDMMediaFileRecord.record_cls = RDMRecordMediaFiles
