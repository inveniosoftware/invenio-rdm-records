# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from marshmallow import INCLUDE, EXCLUDE, Schema as _Schema, fields, missing

from .access import AccessSchemaV1
from .communities import CommunitiesSchemaV1
from .files import FilesSchemaV1
from .metadata import MetadataSchemaV1
from .pids import PIDSSchemaV1
from .relations import RelationsSchemaV1
from .stats import StatsSchemaV1


def get_value(obj, key, default=missing):
    if not isinstance(key, int) and "." in key:
        return _get_value_for_keys(obj, key.split("."), default)
    else:
        return _get_value_for_key(obj, key, default)


def _get_value_for_keys(obj, keys, default):
    if len(keys) == 1:
        return _get_value_for_key(obj, keys[0], default)
    else:
        return _get_value_for_keys(
            _get_value_for_key(obj, keys[0], default), keys[1:], default
        )


def _get_value_for_key(obj, key, default):
    if not hasattr(obj, "__getitem__"):
        return getattr(obj, key, default)
    # NOTE: Here we reverse the order, and do `getattr` first
    try:
        return getattr(obj, key)
    except (KeyError, IndexError, TypeError, AttributeError):
        return obj.get(key, default)


# NOTE: Explicitly use this at the top level of schemas that contain system
# fields (e.g. `record.files`) and even some of their nested values, e.g.
# `record.files.count`
class AttrSchema(_Schema):

    def get_attribute(self, obj, attr, default):
        return get_value(obj, attr, default)

# .vs

# NOTE: Use this one for system fields only
class NestedAttributeField(fields.Nested):

    def get_value(self, obj, attr, accessor=None, default=missing):
        attribute = getattr(self, "attribute", None)
        check_key = attr if attribute is None else attribute
        return get_value(obj, check_key, default)


class RDMRecordSchemaV1(AttrSchema):
    """Record schema."""

    class Meta:
        unknown = EXCLUDE

    field_load_permissions = {
        'files': 'update',
    }

    field_dump_permissions = {
        'files': 'read_files',
    }

    # schema_version = fields.Interger(dump_only=True)
    revision = fields.Integer(attribute='revision_id', dump_only=True)
    id = fields.Str(attribute='recid', dump_only=True)
    concept_id = fields.Str(attribute='conceptrecid', dump_only=True)
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
