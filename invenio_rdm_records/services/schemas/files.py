# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from invenio_records_rest.schemas.fields import SanitizedUnicode
from marshmallow import INCLUDE, Schema, fields, validate


class FileSchema(Schema):
    """File schema."""

    type = fields.String()
    checksum = fields.String()
    size = fields.Integer()
    bucket = fields.String()
    key = fields.String()
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
    items = fields.List(fields.Nested(FileSchema))
