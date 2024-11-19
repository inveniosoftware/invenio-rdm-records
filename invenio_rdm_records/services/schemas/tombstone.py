# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Schemas related to record deletion status and tombstones."""

from invenio_vocabularies.services.schema import VocabularyRelationSchema
from marshmallow import Schema, fields
from marshmallow_utils.fields import ISODateString, SanitizedUnicode

from .parent.access import Agent as BaseAgentSchema


class AgentSchema(BaseAgentSchema):
    """An agent schema, using a string for the ID to allow the "system" user."""

    user = fields.String(required=True)


class RemovalReasonSchema(VocabularyRelationSchema):
    """Schema for the removal reason."""

    id = fields.String(required=True)


class TombstoneSchema(Schema):
    """Schema for the record's tombstone."""

    removal_reason = fields.Nested(RemovalReasonSchema)
    note = SanitizedUnicode()
    removed_by = fields.Nested(AgentSchema, dump_only=True)
    removal_date = ISODateString(dump_only=True)
    citation_text = SanitizedUnicode()
    is_visible = fields.Boolean()


class DeletionStatusSchema(Schema):
    """Schema for the record deletion status."""

    is_deleted = fields.Boolean(dump_only=True)
    status = fields.String(dump_only=True)
