# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record and Draft API."""


from invenio_drafts_resources.records import Draft, Record
from invenio_records.dumpers import ElasticsearchDumper
from invenio_records.models import RecordMetadata
from invenio_records_resources.records.systemfields import IndexField

from .dumpers import EDTFDumperExt
from .models import DraftMetadata


class BibliographicRecord(Record):
    """Bibliographic Record API."""

    model_cls = RecordMetadata

    index = IndexField(
        'rdmrecords-records-record-v1.0.0', search_alias='rdmrecords-records')

    dumper = ElasticsearchDumper(
        extensions=[EDTFDumperExt('metadata.publication_date')])


class BibliographicDraft(Draft):
    """Bibliographic draft API."""

    model_cls = DraftMetadata

    index = IndexField(
        'rdmrecords-drafts-draft-v1.0.0', search_alias='rdmrecords-drafts')

    dumper = ElasticsearchDumper(
        extensions=[EDTFDumperExt('metadata.publication_date')])
