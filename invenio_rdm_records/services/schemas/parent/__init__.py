# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM parent record schema."""

from invenio_drafts_resources.services.records.schema import ParentSchema
from invenio_requests.services.schemas import RequestSchema
from marshmallow import fields, pre_load
from marshmallow_utils.permissions import FieldPermissionsMixin

from .access import ParentAccessSchema
from .communities import CommunitiesSchema


class RDMParentSchema(ParentSchema, FieldPermissionsMixin):
    """Record schema."""

    field_dump_permissions = {
        # omit the 'access' field from dumps, except for users with
        # 'manage' permissions
        "access": "manage",
        # omit 'review' from dumps execpt for users with curate permission
        "review": "curate",
    }

    access = fields.Nested(ParentAccessSchema, dump_only=True)
    review = fields.Nested(RequestSchema)
    communities = fields.Nested(CommunitiesSchema, dump_only=True)

    # TOOD: make nicer
    @pre_load
    def clean(self, data, **kwargs):
        """Removes dump_only fields.

        Why: We want to allow the output of a Schema dump, to be a valid input
             to a Schema load without causing strange issues.
        """
        for name, field in self.fields.items():
            if field.dump_only:
                data.pop(name, None)
        return data


__all__ = ("RDMParentSchema",)
