# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record and Draft API."""

from invenio_communities.records.records.systemfields import CommunitiesField
from invenio_drafts_resources.records import Draft, Record
from invenio_drafts_resources.records.api import ParentRecord as ParentRecordBase
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
from invenio_requests.records.systemfields.relatedrecord import RelatedRecord
from invenio_vocabularies.contrib.affiliations.api import Affiliation
from invenio_vocabularies.contrib.awards.api import Award
from invenio_vocabularies.contrib.funders.api import Funder
from invenio_vocabularies.contrib.subjects.api import Subject
from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.systemfields.relations import CustomFieldsRelation

from . import models
from .dumpers import EDTFDumperExt, EDTFListDumperExt, GrantTokensDumperExt
from .systemfields import HasDraftCheckField, ParentRecordAccessField, RecordAccessField
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
        ]
    )

    # System fields
    schema = ConstantField("$schema", "local://records/parent-v2.0.0.json")

    access = ParentRecordAccessField()

    review = RelatedRecord(
        Request,
        keys=["type", "receiver", "status"],
    )

    communities = CommunitiesField(models.RDMParentCommunity)


#
# Common properties between records and drafts.
#
class CommonFieldsMixin:
    """Common system fields between records and drafts."""

    versions_model_cls = models.RDMVersionsState
    parent_record_cls = RDMParent

    schema = ConstantField("$schema", "local://records/record-v5.0.0.json")

    dumper = SearchDumper(
        extensions=[
            EDTFDumperExt("metadata.publication_date"),
            EDTFListDumperExt("metadata.dates", "date"),
            RelationDumperExt("relations"),
            CustomFieldsDumperExt(fields_var="RDM_CUSTOM_FIELDS"),
        ]
    )

    relations = MultiRelationsField(
        creator_affiliations=PIDNestedListRelation(
            "metadata.creators",
            relation_field="affiliations",
            keys=["name"],
            pid_field=Affiliation.pid,
            cache_key="affiliations",
        ),
        contributor_affiliations=PIDNestedListRelation(
            "metadata.contributors",
            relation_field="affiliations",
            keys=["name"],
            pid_field=Affiliation.pid,
            cache_key="affiliations",
        ),
        funding_funder=PIDListRelation(
            "metadata.funding",
            relation_field="funder",
            keys=["name"],
            pid_field=Funder.pid,
            cache_key="funders",
        ),
        funding_award=PIDListRelation(
            "metadata.funding",
            relation_field="award",
            keys=["title", "number", "identifiers"],
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
        custom=CustomFieldsRelation("RDM_CUSTOM_FIELDS"),
    )

    bucket_id = ModelField(dump=False)

    bucket = ModelField(dump=False)

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


class RDMDraft(CommonFieldsMixin, Draft):
    """RDM draft API."""

    model_cls = models.RDMDraftMetadata

    index = IndexField("rdmrecords-drafts-draft-v5.0.0", search_alias="rdmrecords")

    files = FilesField(
        store=False,
        file_cls=RDMFileDraft,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    has_draft = HasDraftCheckField()

    status = DraftStatus()


RDMFileDraft.record_cls = RDMDraft


#
# Record API
#
class RDMFileRecord(FileRecord):
    """Example record file API."""

    model_cls = models.RDMFileRecordMetadata
    record_cls = None  # defined below


class RDMRecord(CommonFieldsMixin, Record):
    """RDM Record API."""

    model_cls = models.RDMRecordMetadata

    index = IndexField(
        "rdmrecords-records-record-v5.0.0", search_alias="rdmrecords-records"
    )

    files = FilesField(
        store=False,
        file_cls=RDMFileRecord,
        # Don't create
        create=False,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    has_draft = HasDraftCheckField(RDMDraft)

    status = DraftStatus()


RDMFileRecord.record_cls = RDMRecord
