# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record communities schema."""

from invenio_i18n import lazy_gettext as _
from invenio_requests.customizations import CommentEventType
from marshmallow import Schema, ValidationError, fields, validate
from marshmallow_utils.context import context_schema


def validate_communities(value):
    """Validate community count and uniqueness.

    A field ``validate`` callable, not ``@validates``: it runs only after every
    item deserialized, so a malformed entry fails first and ``community["id"]``
    is always present here. Messages are wrapped in a list because the field's
    ``validate`` list combines them through marshmallow's ``And``, which would
    otherwise split a lazy_gettext string character by character.
    """
    max_number = context_schema.get()["max_number"]
    if max_number < len(value):
        raise ValidationError(
            [
                _(
                    "Too many communities passed, {max_number} max allowed.".format(
                        max_number=max_number
                    )
                )
            ]
        )

    uniques = set()
    duplicated = set()
    for community in value:
        com_id = community["id"]
        if com_id in uniques:
            duplicated.add(com_id)
        uniques.add(com_id)

    if duplicated:
        raise ValidationError(
            [_("Duplicated communities {com_ids}.".format(com_ids=duplicated))]
        )


class CommunitySchema(Schema):
    """Schema to define a community id."""

    id = fields.String(required=True)
    comment = fields.Nested(CommentEventType.marshmallow_schema)
    require_review = fields.Boolean()


class RecordCommunitiesSchema(Schema):
    """Record communities schema."""

    communities = fields.List(
        fields.Nested(CommunitySchema),
        validate=[validate.Length(min=1), validate_communities],
        required=True,
    )
