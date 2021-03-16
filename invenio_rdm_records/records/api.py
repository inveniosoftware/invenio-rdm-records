# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record and Draft API."""

from invenio_drafts_resources.records import Draft, Record
from invenio_drafts_resources.records.api import \
    ParentRecord as ParentRecordBase
from invenio_pidstore.models import PIDStatus
from invenio_records.dumpers import ElasticsearchDumper
from invenio_records.dumpers.relations import RelationDumperExt
from invenio_records.systemfields import ConstantField, ModelField, \
    RelationsField
from invenio_records_resources.records.api import RecordFile as RecordFileBase
from invenio_records_resources.records.systemfields import FilesField, \
    IndexField, PIDListRelation
from invenio_vocabularies.records.api import Vocabulary
from werkzeug.local import LocalProxy

from . import models
from .dumpers import EDTFDumperExt, EDTFListDumperExt, GrantTokensDumperExt
from .systemfields import HasDraftCheckField, IsPublishedField, \
    ParentRecordAccessField, RecordAccessField


#
# Parent record API
#
class RDMParent(ParentRecordBase):
    """Example parent record."""

    # Configuration
    model_cls = models.RDMParentMetadata

    dumper = ElasticsearchDumper(
        extensions=[
            GrantTokensDumperExt("access.grant_tokens"),
        ]
    )

    # System fields
    schema = ConstantField(
        '$schema', 'http://localhost/schemas/records/parent-v1.0.0.json')

    access = ParentRecordAccessField()


#
# Common properties between records and drafts.
#
class CommonFieldsMixin:
    """Common system fields between records and drafts."""

    versions_model_cls = models.RDMVersionsState
    parent_record_cls = RDMParent

    schema = ConstantField(
       '$schema', 'http://localhost/schemas/records/record-v2.0.0.json')

    dumper = ElasticsearchDumper(
        extensions=[
            EDTFDumperExt('metadata.publication_date'),
            EDTFListDumperExt("metadata.dates", "date"),
            RelationDumperExt('relations'),
        ]
    )

    relations = RelationsField(
        languages=PIDListRelation(
            'metadata.languages',
            attrs=['id', 'title'],
            pid_field=Vocabulary.pid.with_type_ctx('languages')
        ),
    )

    bucket_id = ModelField(dump=False)

    bucket = ModelField(dump=False)

    access = RecordAccessField()

    # We redefine the property as we extend the `PIDStatusCheckField` to dump
    # the property in ES in order to be available for aggregation
    is_published = IsPublishedField(status=PIDStatus.REGISTERED)


#
# Draft API
#
class DraftFile(RecordFileBase):
    """File associated with a draft."""

    model_cls = models.DraftFile
    record_cls = LocalProxy(lambda: RDMDraft)


class RDMDraft(CommonFieldsMixin, Draft):
    """RDM draft API."""

    model_cls = models.RDMDraftMetadata

    index = IndexField(
        "rdmrecords-drafts-draft-v2.0.0", search_alias="rdmrecords"
    )

    files = FilesField(
        store=False,
        file_cls=DraftFile,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    has_draft = HasDraftCheckField()


#
# Record API
#
class RecordFile(RecordFileBase):
    """Example record file API."""

    model_cls = models.RecordFile
    record_cls = LocalProxy(lambda: RDMRecord)


class RDMRecord(CommonFieldsMixin, Record):
    """RDM Record API."""

    model_cls = models.RDMRecordMetadata

    index = IndexField(
        "rdmrecords-records-record-v2.0.0", search_alias="rdmrecords-records"
    )

    files = FilesField(
        store=False,
        file_cls=RecordFile,
        # Don't create
        create=False,
        # Don't delete, we'll manage in the service
        delete=False,
    )

    has_draft = HasDraftCheckField(RDMDraft)
