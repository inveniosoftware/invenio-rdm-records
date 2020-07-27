# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record and Draft models."""

from invenio_db import db
from invenio_drafts_resources.drafts import DraftBase, DraftMetadataBase
from invenio_records.api import Record
from invenio_records.models import RecordMetadata, RecordMetadataBase


class BibliographicRecordDraftMetadata(db.Model, DraftMetadataBase):
    """Represent a bibliographic record draft metadata."""

    __tablename__ = 'bibl_drafts_metadata'


class BibliographicRecordDraft(DraftBase):
    """Bibliographic draft API."""

    model_cls = BibliographicRecordDraftMetadata


# class BibliographicRecordMetadata(db.Model, RecordMetadataBase):
#     """Represent a bibliographic record metadata."""

#     __tablename__ = 'records_metadata'


class BibliographicRecord(Record):
    """Bibliographic Record API."""

    # FIXME: Cannot due to collision with old implementation.
    # model_cls = BibliographicRecordMetadata
    model_cls = RecordMetadata
