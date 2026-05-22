# SPDX-FileCopyrightText: 2021-2024 CERN.
# SPDX-License-Identifier: MIT

"""Schemas for parameter parsing."""

from invenio_drafts_resources.resources.records.args import SearchRequestArgsSchema
from marshmallow import fields


class RDMSearchRequestArgsSchema(SearchRequestArgsSchema):
    """Extend schema with CSL fields."""

    style = fields.Str()
    locale = fields.Str()
    status = fields.Str()
    include_deleted = fields.Bool()
    shared_with_me = fields.Bool()
