# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM parent record schema."""

from invenio_drafts_resources.services.records.schema import ParentSchema
from marshmallow import fields
from marshmallow_utils.permissions import FieldPermissionsMixin

from .access import ParentAccessSchema


class RDMParentSchema(ParentSchema, FieldPermissionsMixin):
    """Record schema."""

    # omit the 'access' field from dumps, except for users with
    # 'manage' permissions
    field_dump_permissions = {
        "access": "manage",
    }

    access = fields.Nested(ParentAccessSchema)


__all__ = ("RDMParentSchema",)
