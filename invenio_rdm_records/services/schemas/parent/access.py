# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Access schema for RDM parent record."""


from datetime import timezone

from flask_babelex import lazy_gettext as _
from marshmallow import Schema, fields, validate
from marshmallow_utils.fields import SanitizedUnicode, TZDateTime


class Grant(Schema):
    """Schema for an access grant."""

    subject = fields.String()
    id = fields.String()
    level = fields.String()


class SecretLink(Schema):
    """Schema for a secret link."""

    id = fields.String(dump_only=True)
    created_at = TZDateTime(
        timezone=timezone.utc, format='iso', required=False, dump_only=True)
    expires_at = TZDateTime(
        timezone=timezone.utc, format='iso', required=False)
    permission = fields.String(
        required=False,
        validate=validate.OneOf(["view", "preview", "edit"]))
    token = SanitizedUnicode(dump_only=True)


class Agent(Schema):
    """An agent schema."""

    user = fields.Integer(required=True)


class ParentAccessSchema(Schema):
    """Access schema."""

    grants = fields.List(fields.Nested(Grant))
    owned_by = fields.List(fields.Nested(Agent))
    links = fields.List(fields.Nested(SecretLink))
