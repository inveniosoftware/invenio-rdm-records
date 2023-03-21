# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Schema for record statistics."""

from marshmallow import Schema, fields


class PartialStatsSchema(Schema):
    """Schema for a part of the record statistics.

    This fits both the statistics for "this version" as well as
    "all versions", because they have the same shape.
    """

    views = fields.Int()
    unique_views = fields.Int()
    downloads = fields.Int()
    unique_downloads = fields.Int()
    data_volume = fields.Float()


class StatsSchema(Schema):
    """Schema for the entire record statistics."""

    this_version = fields.Nested(PartialStatsSchema)
    all_versions = fields.Nested(PartialStatsSchema)
