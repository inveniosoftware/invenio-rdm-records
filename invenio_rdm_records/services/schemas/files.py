# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from marshmallow import Schema, fields
from marshmallow_utils.fields import SanitizedUnicode


class FileSchema(Schema):
    """File schema."""

    type = fields.String()
    checksum = fields.String()
    size = fields.Integer()
    key = SanitizedUnicode()
    version_id = SanitizedUnicode()
    bucket_id = SanitizedUnicode()
    mimetype = SanitizedUnicode()
    storage_class = SanitizedUnicode()

    # TODO (Alex): See how this fits with using the refactored Linker
    # links = fields.Method('get_links')

    # def get_links(self, obj):
    #     """Get links."""
    #     return {
    #         'self': api_link_for(
    #             'object', bucket=obj['bucket'], key=obj['key'])
    #     }


class FilesSchema(Schema):
    """Files metadata schema."""

    enabled = fields.Bool()
    default_preview = SanitizedUnicode()
    order = fields.List(SanitizedUnicode())

    # TODO: Used to store metadata for files (e.g. description, width/height)
    # meta = fields.Dict(
    #     keys=SanitizedUnicode(),
    #     values=fields.Raw(),
    # )
    # entries = fields.Dict(
    #     keys=SanitizedUnicode(),
    #     values=fields.Nested(FileSchema),
    #     dump_only=True,
    # )
