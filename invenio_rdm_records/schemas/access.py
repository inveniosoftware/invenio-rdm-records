# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

import arrow
from invenio_records_rest.schemas.fields import DateString, SanitizedUnicode
from marshmallow import Schema, ValidationError, fields, validate, validates

from .utils import validate_entry


class AccessSchemaV1(Schema):
    """Access schema."""

    metadata_restricted = fields.Bool(required=True)
    files_restricted = fields.Bool(required=True)
    owners = fields.List(
        fields.Integer, validate=validate.Length(min=1), required=True)
    created_by = fields.Integer(required=True)
    embargo_date = DateString()
    contact = SanitizedUnicode(data_key="contact", attribute="contact")
    access_right = SanitizedUnicode(required=True)

    @validates('embargo_date')
    def validate_embargo_date(self, value):
        """Validate that embargo date is in the future."""
        if arrow.get(value).date() <= arrow.utcnow().date():
            raise ValidationError(
                _('Embargo date must be in the future.'),
                field_names=['embargo_date']
            )

    @validates('access_right')
    def validate_access_right(self, value):
        """Validate that access right is one of the allowed ones."""
        access_right_key = {'access_right': value}
        validate_entry('access_right', access_right_key)
