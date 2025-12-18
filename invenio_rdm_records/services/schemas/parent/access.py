# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Access schema for RDM parent record."""

# TODO: Replace with invenio_records_resources.services.base.schema import *

from datetime import timezone

from marshmallow import Schema, fields, validate
from marshmallow.validate import OneOf
from marshmallow_utils.fields import (
    ISODateString,
    SanitizedUnicode,
    TZDateTime,
)
from marshmallow_utils.permissions import FieldPermissionsMixin

from ..fields import SanitizedHTML


class GrantSubject(Schema):
    """Schema for a grant subject."""

    id = fields.String(required=True)
    type = fields.String(
        required=True, validate=validate.OneOf(["user", "role", "system_role"])
    )


class Grant(Schema):
    """Schema for an access grant."""

    permission = fields.String(required=True)
    subject = fields.Nested(GrantSubject, required=True)
    origin = fields.String(required=False)
    message = SanitizedUnicode()
    notify = fields.Bool()


class Grants(Schema):
    """Grants Schema."""

    grants = fields.List(
        fields.Nested(Grant),
        # max is on purpose to limit the max number of additions/changes/
        # removals per request as they all run in a single transaction and
        # requires resources to hold.
        validate=validate.Length(min=1, max=100),
    )


class SecretLink(Schema):
    """Schema for a secret link."""

    id = fields.String(dump_only=True)
    created_at = TZDateTime(
        timezone=timezone.utc, format="iso", required=False, dump_only=True
    )
    expires_at = ISODateString(required=False)
    permission = fields.String(
        required=False, validate=validate.OneOf(["view", "preview", "edit"])
    )
    description = SanitizedUnicode(required=False)
    origin = fields.String(required=False)
    token = SanitizedUnicode(dump_only=True)


class Agent(Schema):
    """An agent schema."""

    user = fields.String(required=True)


class AccessSettingsSchema(Schema):
    """Schema for a record's access settings."""

    # enabling/disabling guests or users to send access requests
    allow_user_requests = fields.Boolean()
    allow_guest_requests = fields.Boolean()

    accept_conditions_text = SanitizedHTML(allow_none=True)
    secret_link_expiration = fields.Integer(validate=validate.Range(max=365, min=0))


class ParentAccessSchema(Schema, FieldPermissionsMixin):
    """Access schema."""

    field_dump_permissions = {
        # omit fields from dumps except for users with 'manage' permissions
        # allow only 'settings' and 'owned_by'
        "grants": "manage",
        "links": "manage",
    }

    grants = fields.List(fields.Nested(Grant))
    owned_by = fields.Nested(Agent)
    links = fields.List(fields.Nested(SecretLink))
    settings = fields.Nested(AccessSettingsSchema)


class RequestAccessSchema(Schema):
    """Access request schema."""

    permission = fields.Constant("view")
    email = fields.Email()
    full_name = SanitizedUnicode()
    message = SanitizedUnicode()
    consent_to_share_personal_data = fields.String(validate=OneOf(["true", "false"]))
