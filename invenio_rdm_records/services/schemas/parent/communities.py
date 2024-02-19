# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Community schema."""

from invenio_communities.communities.schema import CommunitySchema
from marshmallow import Schema, fields, post_dump


class CommunitiesSchema(Schema):
    """Communities schema."""

    ids = fields.List(fields.String())
    default = fields.String(attribute="default.id")
    entries = fields.List(fields.Nested(CommunitySchema))

    @post_dump
    def clear_none_values(self, data, **kwargs):
        """Remove empty values from the dump."""
        return {k: v for k, v in data.items() if v}
