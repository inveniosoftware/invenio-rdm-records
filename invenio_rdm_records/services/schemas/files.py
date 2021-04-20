# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
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

    def get_attribute(self, obj, attr, default):
        """Override how attributes are retrieved when dumping.

        NOTE: We have to access by attribute because although we are loading
              from an external pure dict, but we are dumping from a data-layer
              object whose fields should be accessed by attributes and not
              keys. Access by key runs into FilesManager key access protection
              and raises.
        """
        value = getattr(obj, attr, default)

        if attr == "default_preview" and value is None:
            # NOTE: Might be that the "real" solution is to have
            #       default_preview default to "" in records-resources, but
            #       this way at least we save some bytes.
            return default

        return value

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
