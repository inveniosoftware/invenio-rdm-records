# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM parent record schema."""

from flask import current_app
from invenio_drafts_resources.services.records.schema import ParentSchema
from invenio_i18n import lazy_gettext as _
from invenio_requests.services.schemas import GenericRequestSchema
from marshmallow import ValidationError, fields, post_dump, pre_load
from marshmallow_utils.fields import NestedAttribute, SanitizedUnicode
from marshmallow_utils.permissions import FieldPermissionsMixin

from ..pids import PIDSchema
from .access import ParentAccessSchema
from .communities import CommunitiesSchema


def validate_scheme(scheme):
    """Validate a PID scheme."""
    if scheme not in current_app.config["RDM_PARENT_PERSISTENT_IDENTIFIERS"]:
        raise ValidationError(
            _("Invalid persistent identifier scheme {scheme}.".format(scheme=scheme))
        )


class RDMParentSchema(ParentSchema, FieldPermissionsMixin):
    """Record schema."""

    field_dump_permissions = {
        # omit 'review' from dumps except for users with curate permission
        "review": "review",
        # omit 'is_verified' from dumps except for users with moderate permission
        "is_verified": "moderate",
    }

    access = fields.Nested(ParentAccessSchema, dump_only=True)
    review = fields.Nested(GenericRequestSchema, allow_none=False)
    communities = NestedAttribute(CommunitiesSchema, dump_only=True)

    pids = fields.Dict(
        keys=SanitizedUnicode(validate=validate_scheme),
        values=fields.Nested(PIDSchema),
        dump_only=True,
    )
    is_verified = fields.Boolean(dump_only=True)

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
        if data.get("review", None) is None:
            data.pop("review", None)
        return data

    @post_dump()
    def pop_review_if_none(self, data, many, **kwargs):
        """Clear review if None."""
        if data.get("review", None) is None:
            data.pop("review", None)
        return data


__all__ = ("RDMParentSchema",)
