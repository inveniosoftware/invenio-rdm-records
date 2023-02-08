# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record communities schema."""

from marshmallow import EXCLUDE, Schema, fields, pre_load, validate

from invenio_rdm_records.services.errors import MaxNumberCommunitiesExceeded


class CommunitySchema(Schema):
    """Schema to define a community id."""

    id = fields.String()


class RecordCommunitiesSchema(Schema):
    """Record communities schema."""

    communities = fields.List(
        fields.Nested(CommunitySchema), validate=validate.Length(min=1)
    )

    @pre_load
    def _check_max_size(self, data, **kwargs):
        max_number = self.context.get("max_number")
        if max_number < len(data["communities"]):
            raise MaxNumberCommunitiesExceeded(max_number)
        return data
