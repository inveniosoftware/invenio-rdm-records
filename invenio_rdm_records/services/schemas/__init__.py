# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from invenio_drafts_resources.services.records.schema import RecordSchema
from marshmallow import EXCLUDE, INCLUDE, Schema, fields, missing

from .access import AccessSchema
from .metadata import MetadataSchema
from .pids import PIDSchema


# NOTE: Use this one for system fields only
class AttributeAccessorFieldMixin:
    """Marshmallow field mixin for attribute-based serialization."""

    def get_value(self, obj, attr, accessor=None, default=missing):
        """Return the value for a given key from an object attribute."""
        attribute = getattr(self, "attribute", None)
        check_key = attr if attribute is None else attribute
        return getattr(obj, check_key, default)


class NestedAttribute(fields.Nested, AttributeAccessorFieldMixin):
    """Nested object attribute field."""


class RDMRecordSchema(RecordSchema):
    """Record schema."""

    class Meta:
        """Meta class."""

        unknown = EXCLUDE

    field_load_permissions = {
        'files': 'update',
    }

    field_dump_permissions = {
        'files': 'read_files',
    }

    id = fields.Str()
    # pid
    conceptid = fields.Str()
    # conceptpid
    pids = fields.List(NestedAttribute(PIDSchema))
    metadata = NestedAttribute(MetadataSchema)
    # ext = fields.Method('dump_extensions', 'load_extensions')
    # tombstone
    # provenance
    access = NestedAttribute(AccessSchema)
    # files = NestedAttribute(FilesSchema, dump_only=True)
    # notes = fields.List(fields.Nested(InternalNoteSchema))
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
    revision = fields.Integer(dump_only=True)

    # communities = NestedAttribute(CommunitiesSchema)
    # stats = NestedAttribute(StatsSchema, dump_only=True)
    # relations = NestedAttribute(RelationsSchema, dump_only=True)
    # schema_version = fields.Interger(dump_only=True)

    # def dump_extensions(self, obj):
    #     """Dumps the extensions value.

    #     :params obj: invenio_records_files.api.Record instance
    #     """
    #     current_app_metadata_extensions = (
    #         current_app.extensions['invenio-rdm-records'].metadata_extensions
    #     )
    #     ExtensionSchema = current_app_metadata_extensions.to_schema()
    #     return ExtensionSchema().dump(obj.get('extensions', {}))

    # def load_extensions(self, value):
    #     """Loads the 'extensions' field.

    #     :params value: content of the input's 'extensions' field
    #     """
    #     current_app_metadata_extensions = (
    #         current_app.extensions['invenio-rdm-records'].metadata_extensions
    #     )
    #     ExtensionSchema = current_app_metadata_extensions.to_schema()

    #     return ExtensionSchema().load(value)


__all__ = (
    'RDMRecordSchema',
)
