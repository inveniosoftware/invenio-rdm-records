# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

import arrow
from flask_babelex import lazy_gettext as _
from marshmallow import Schema, ValidationError, fields, validates, \
    validates_schema
from marshmallow_utils.fields import ISODateString, SanitizedUnicode
from marshmallow_utils.fields.nestedattr import NestedAttribute


class EmbargoSchema(Schema):
    """Schema for an embargo on the record."""

    active = fields.Bool(allow_none=True, missing=None)
    until = ISODateString(allow_none=True, missing=None)
    reason = SanitizedUnicode(allow_none=True, missing=None)

    @validates_schema
    def validate_embargo(self, data, **kwargs):
        """Validate that the properties are consistent with each other."""
        if data.get("until") is not None:
            until_date = arrow.get(data.get("until"))
        else:
            until_date = None

        if data.get("active", False):
            # 'active' is set to True => 'until' must be set to a future date
            if until_date is None or until_date < arrow.utcnow():
                raise ValidationError(
                    _("Embargo end date must be set to a future date "
                      "if active is True."),
                    field_name="until",
                )

        elif data.get("active", None) is not None:
            # 'active' is set to False => 'until' must be either set to a past
            #                             date, or not set at all
            if until_date is not None and until_date > arrow.utcnow():
                raise ValidationError(
                    _("Embargo end date must be unset or in the past "
                      "if active is False."),
                    field_name="until",
                )


class AccessSchema(Schema):
    """Access schema."""

    record = SanitizedUnicode(required=True)
    files = SanitizedUnicode(required=True)
    embargo = NestedAttribute(EmbargoSchema)
    status = SanitizedUnicode(dump_only=False)

    def validate_protection_value(self, value, field_name):
        """Check that the protection value is valid."""
        if value not in ["public", "restricted"]:
            raise ValidationError(
                _(f"'{field_name}' must be either 'public' or 'restricted'"),
                "record"
            )

    def get_attribute(self, obj, key, default):
        """Override from where we get attributes when serializing."""
        if key in ["record", "files"]:
            return getattr(obj.protection, key, default)
        elif key == "status":
            return obj.status.value
        return getattr(obj, key, default)

    @validates("record")
    def validate_record_protection(self, value):
        """Validate the record protection value."""
        self.validate_protection_value(value, "record")

    @validates("files")
    def validate_files_protection(self, value):
        """Validate the files protection value."""
        self.validate_protection_value(value, "files")
