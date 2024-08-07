# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Schemas for parameter parsing."""

from invenio_drafts_resources.resources.records.args import SearchRequestArgsSchema
from marshmallow import fields


class RDMSearchRequestArgsSchema(SearchRequestArgsSchema):
    """Extend schema with CSL fields."""

    style = fields.Str()
    locale = fields.Str()
    status = fields.Str()
    include_deleted = fields.Bool()
