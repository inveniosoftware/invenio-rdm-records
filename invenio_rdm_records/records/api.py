# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record and Draft API."""

from invenio_db import db
from invenio_drafts_resources.records import Draft, Record
from invenio_records.dumpers import ElasticsearchDumper
from invenio_records.dumpers.relations import RelationDumperExt
from invenio_records.systemfields import ModelField, RelationsField
from invenio_records_resources.records.api import RecordFile as RecordFileBase
from invenio_records_resources.records.systemfields import FilesField, \
    IndexField, PIDListRelation
from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyType
from werkzeug.local import LocalProxy

from . import models
from .dumpers import EDTFDumperExt, EDTFListDumperExt


class Language(Vocabulary):
    """Language vocabulary record class."""

    @classmethod
    def get_record(cls, id_, with_deleted=False):
        """Get a language record."""
        with db.session.no_autoflush:
            query = cls.model_cls.query.filter(
                # TODO: move this to the base Vocabulary record class
                cls.model_cls.vocabulary_type.has(name='languages'),
                cls.model_cls.id == id_,
            )
            if not with_deleted:
                query = query.filter(cls.model_cls.is_deleted != True)  # noqa
            obj = query.one()
            return cls(obj.data, model=obj)


class RecordFile(RecordFileBase):
    """Example record file API."""

    model_cls = models.RecordFile
    record_cls = LocalProxy(lambda: BibliographicRecord)


class BibliographicRecord(Record):
    """Bibliographic Record API."""

    model_cls = models.RecordMetadata

    index = IndexField(
        "rdmrecords-records-record-v1.0.0", search_alias="rdmrecords-records"
    )

    dumper = ElasticsearchDumper(
        extensions=[
            EDTFDumperExt('metadata.publication_date'),
            EDTFListDumperExt("metadata.dates", "date"),
            RelationDumperExt('relations'),
        ])

    relations = RelationsField(
        languages=PIDListRelation(
            'metadata.languages', attrs=['metadata'], pid_field=Language.pid),
    )

    files = FilesField(
        store=False, file_cls=RecordFile,
        # Don't create
        create=False,
        # Don't delete, we'll manage in the service
        delete=False,
    )
    bucket_id = ModelField(dump=False)
    bucket = ModelField(dump=False)


class DraftFile(RecordFileBase):
    """Example record file API."""

    model_cls = models.DraftFile
    record_cls = LocalProxy(lambda: BibliographicDraft)


class BibliographicDraft(Draft):
    """Bibliographic draft API."""

    model_cls = models.DraftMetadata

    index = IndexField(
        "rdmrecords-drafts-draft-v1.0.0", search_alias="rdmrecords-drafts"
    )

    dumper = ElasticsearchDumper(
        extensions=[
            EDTFDumperExt('metadata.publication_date'),
            EDTFListDumperExt("metadata.dates", "date"),
            RelationDumperExt('relations'),
        ])

    relations = RelationsField(
        languages=PIDListRelation(
            'metadata.languages', attrs=['metadata'], pid_field=Language.pid),
    )

    files = FilesField(
        store=False, file_cls=DraftFile,
        # Don't delete, we'll manage in the service
        delete=False,
    )
    bucket_id = ModelField(dump=False)
    bucket = ModelField(dump=False)
