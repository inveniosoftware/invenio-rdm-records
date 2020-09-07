# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from marshmallow import INCLUDE, Schema, fields

from .access import AccessSchemaV1
from .communities import CommunitiesSchemaV1
from .files import FilesSchemaV1
from .metadata import MetadataSchemaV1
from .pids import PIDSSchemaV1
from .relations import RelationsSchemaV1
from .stats import StatsSchemaV1


class RDMRecordSchemaV1(Schema):
    """Record schema."""

    class Meta:
        unknown = INCLUDE

    field_load_permissions = {
        'files': 'update',
    }

    field_dump_permissions = {
        'files': 'read_files',
    }

    # schema_version = fields.Interger(dump_only=True)
    revision = fields.Integer(data_key='revision_id', dump_only=True)
    id = fields.Str(data_key='recid', dump_only=True)
    concept_id = fields.Str(data_key='conceptrecid', dump_only=True)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)

    # status = fields.Str(dump_only=True)

    metadata = fields.Nested(MetadataSchemaV1)
    access = fields.Nested(AccessSchemaV1)
    # files = fields.Nested(FilesSchemaV1, dump_only=True)
    # communities = fields.Nested(CommunitiesSchemaV1)
    # pids = fields.Nested(PIDSSchemaV1)
    # stats = fields.Nested(StatsSchemaV1, dump_only=True)
    # relations = fields.Nested(RelationsSchemaV1, dump_only=True)


__all__ = (
    'RDMRecordSchemaV1',
)
