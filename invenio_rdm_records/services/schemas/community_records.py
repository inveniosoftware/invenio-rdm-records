# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record communities schema."""

from marshmallow import Schema, fields, post_load, validate
from marshmallow_utils.fields import StrippedHTML

from invenio_rdm_records.services.errors import MaxNumberCommunitiesExceeded


class CommunitySchema(Schema):
    """Schema to define a community id."""

    id = fields.String(required=True)
    comment = StrippedHTML()
    require_review = fields.Boolean()


class RecordCommunitiesSchema(Schema):
    """Record communities schema."""

    communities = fields.List(
        fields.Nested(CommunitySchema), validate=validate.Length(min=1), required=True
    )

    @post_load
    def _check_max_size(self, data, **kwargs):
        max_number = self.context["max_number"]
        if max_number < len(data["communities"]):
            raise MaxNumberCommunitiesExceeded(max_number)
        return data
