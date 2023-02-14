# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Community records schema."""

from marshmallow import Schema, fields, post_load, validate

from invenio_rdm_records.services.errors import MaxNumberOfRecordsExceed


class RecordSchema(Schema):
    """Schema to define a community id."""

    id = fields.String()


class CommunityRecordsSchema(Schema):
    """Record communities schema."""

    records = fields.List(
        fields.Nested(RecordSchema), validate=validate.Length(min=1), required=True
    )

    @post_load
    def _check_max_size(self, data, **kwargs):
        max_number = self.context["max_number"]
        if max_number < len(data["records"]):
            raise MaxNumberOfRecordsExceed(max_number)
        return data
