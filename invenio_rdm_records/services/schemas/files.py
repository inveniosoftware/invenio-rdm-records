# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2023 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from invenio_vocabularies.services.schema import (
    VocabularyRelationSchema as VocabularySchema,
)
from marshmallow import Schema, fields, pre_load
from marshmallow_utils.fields import NestedAttribute, SanitizedUnicode
from marshmallow_utils.permissions import FieldPermissionsMixin


class FileSchema(Schema):
    """File schema."""

    # File fields
    id = fields.String(attribute="file.id")
    checksum = fields.String(attribute="file.checksum")
    ext = fields.String(attribute="file.ext")
    size = fields.Integer(attribute="file.size")
    mimetype = fields.String(attribute="file.mimetype")

    # FileRecord fields
    key = SanitizedUnicode()
    metadata = fields.Dict()


class FilesSchema(Schema, FieldPermissionsMixin):
    """Files metadata schema."""

    field_dump_permissions = {
        "count": "read_files",
        "default_preview": "read_files",
        "entries": "read_files",
        "order": "read_files",
        "total_bytes": "read_files",
    }

    enabled = fields.Bool()
    default_preview = SanitizedUnicode(allow_none=True)
    order = fields.List(SanitizedUnicode())

    count = fields.Integer(dump_only=True)
    total_bytes = fields.Integer(dump_only=True)

    entries = fields.Dict(
        keys=SanitizedUnicode(),
        values=NestedAttribute(FileSchema),
        dump_only=True,
    )

    @pre_load
    def clean(self, data, **kwargs):
        """Removes dump_only fields.

        Why: We want to allow the output of a Schema dump, to be a valid input to a Schema load without causing strange issues.
        """
        for name, field in self.fields.items():
            if field.dump_only:
                data.pop(name, None)
        return data

    def get_attribute(self, obj, attr, default):
        """Override how attributes are retrieved when dumping.

        NOTE: We have to access by attribute because although we are loading
              from an external pure dict, but we are dumping from a data-layer
              object whose fields should be accessed by attributes and not
              keys. Access by key runs into FilesManager key access protection
              and raises.
        """
        value = getattr(obj, attr, default)

        if attr == "default_preview" and not value:
            return default

        return value


class MediaFileSchema(FileSchema):
    """Media file schema."""

    language = fields.Nested(VocabularySchema)
