# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

import arrow
from flask_babelex import lazy_gettext as _
from marshmallow import Schema, ValidationError, fields, validates, \
    validates_schema
from marshmallow_utils.fields import SanitizedUnicode
from marshmallow_utils.permissions import FieldPermissionsMixin

from .utils import ISODateString


class Grant(Schema):
    """Schema for an access grant."""

    subject = fields.String()
    id = fields.String()
    level = fields.String()


class Agent(Schema):
    """An agent schema."""

    user = fields.Integer(required=True)


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


class AccessSchema(Schema, FieldPermissionsMixin):
    """Access schema."""

    # TODO: we don't want 'owned_by' to be set by the users
    #       but if we don't allow it to be specified, we run
    #       into problems while publishing drafts
    field_load_permissions = {
        # "owned_by": "disabled",
    }

    # omit the grants from dumps, except for users with the
    # 'manage' permission
    field_dump_permissions = {
        "grants": "manage",
    }

    record = SanitizedUnicode(required=True)
    files = SanitizedUnicode(required=True)
    owned_by = fields.List(fields.Nested(Agent))
    embargo = fields.Nested(EmbargoSchema)
    # TODO re-enable when the grants are ready
    # grants = fields.List(fields.Nested(Grant))

    def validate_protection_value(self, value, field_name):
        """Check that the protection value is valid."""
        if value not in ["public", "restricted"]:
            raise ValidationError(
                _("'{}' must be either 'public' or 'restricted'").format(
                    field_name
                ),
                "record"
            )

    @validates("record")
    def validate_record_protection(self, value):
        """Validate the record protection value."""
        self.validate_protection_value(value, "record")

    @validates("files")
    def validate_files_protection(self, value):
        """Validate the files protection value."""
        self.validate_protection_value(value, "files")
