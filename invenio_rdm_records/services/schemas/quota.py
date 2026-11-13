# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-FileCopyrightText: 2025 Graz University of Technology.
# SPDX-FileCopyrightText: 2026 California Institute of Technology.
# SPDX-License-Identifier: MIT

"""Schemas related to storage quotas."""

from marshmallow import Schema, fields, validate
from marshmallow_utils.fields import SanitizedUnicode


class QuotaSchema(Schema):
    """Storage quota schema."""

    quota_size = fields.Integer(required=True)
    max_file_size = fields.Integer(required=True)
    notes = SanitizedUnicode(dump_default="")


class UserQuotaSchema(QuotaSchema):
    """Storage quota schema for users.

    ``max_additional_quota_size`` is optional: if omitted, the stored value is left
    unchanged; if explicitly ``null``, the user falls back to the configured default.
    """

    max_additional_quota_size = fields.Integer(
        allow_none=True, validate=validate.Range(min=0)
    )
