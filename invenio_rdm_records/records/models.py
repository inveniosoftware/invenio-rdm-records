# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record and Draft database models."""

from invenio_db import db
from invenio_drafts_resources.records import DraftMetadataBase
from invenio_files_rest.models import Bucket
from invenio_records.models import RecordMetadataBase
from invenio_records_resources.records.models import RecordFileBase
from sqlalchemy_utils.types import UUIDType


class RDMRecordMetadata(db.Model, RecordMetadataBase):
    """Represent a bibliographic record metadata."""

    __tablename__ = 'rdm_records_metadata'

    # Enable versioning
    __versioned__ = {}

    bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id))
    bucket = db.relationship(Bucket)


class RecordFile(db.Model, RecordFileBase):
    """File associated with a record."""

    record_model_cls = RDMRecordMetadata

    __tablename__ = 'rdm_records_files'


class DraftMetadata(db.Model, DraftMetadataBase):
    """Draft metadata for a record."""

    __tablename__ = 'rdm_drafts_metadata'

    bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id))
    bucket = db.relationship(Bucket)


class DraftFile(db.Model, RecordFileBase):
    """File associated with a draft."""

    record_model_cls = DraftMetadata

    __tablename__ = 'rdm_drafts_files'
