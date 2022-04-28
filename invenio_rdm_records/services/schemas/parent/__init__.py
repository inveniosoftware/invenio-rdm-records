# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM parent record schema."""

from invenio_drafts_resources.services.records.schema import ParentSchema
from invenio_requests.services.schemas import GenericRequestSchema
from marshmallow import fields, post_dump, pre_load
from marshmallow_utils.permissions import FieldPermissionsMixin

from .access import ParentAccessSchema
from .communities import CommunitiesSchema


class RDMParentSchema(ParentSchema, FieldPermissionsMixin):
    """Record schema."""

    field_dump_permissions = {
        # omit the 'access' field from dumps, except for users with
        # 'manage' permissions
        "access": "manage",
        # omit 'review' from dumps except for users with curate permission
        "review": "review",
    }

    access = fields.Nested(ParentAccessSchema, dump_only=True)
    review = fields.Nested(GenericRequestSchema, allow_none=False)
    communities = fields.Nested(CommunitiesSchema, dump_only=True)

    # TODO: move to a reusable place (taken from records-resources)
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

    @pre_load
    def clean_review(self, data, **kwargs):
        """Clear review if None."""
        # draft.parent.review returns None when not set, causing the serializer
        # to dump {'review': None}. As a workaround we pop it if it's none
        # here.
        if data.get('review', None) is None:
            data.pop('review', None)
        return data

    @post_dump()
    def pop_review_if_none(self, data, many, **kwargs):
        """Clear review if None."""
        if data.get('review', None) is None:
            data.pop('review', None)
        return data


__all__ = ("RDMParentSchema",)
