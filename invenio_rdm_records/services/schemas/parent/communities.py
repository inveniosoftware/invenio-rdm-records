# SPDX-FileCopyrightText: 2021-2024 CERN.
# SPDX-License-Identifier: MIT

"""Community schema."""

from invenio_communities.communities.schema import CommunitySchema
from marshmallow import Schema, fields, post_dump


class CommunitiesSchema(Schema):
    """Communities schema."""

    ids = fields.List(fields.String())
    default = fields.String(attribute="default.id", allow_none=True)
    entries = fields.List(fields.Nested(CommunitySchema))

    @post_dump
    def clear_none_values(self, data, **kwargs):
        """Remove empty values from the dump."""
        return {k: v for k, v in data.items() if v}
