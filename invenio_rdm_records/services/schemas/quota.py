# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-FileCopyrightText: 2025 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Schemas related to record deletion status and tombstones."""

from marshmallow import Schema, fields
from marshmallow_utils.fields import SanitizedUnicode


class QuotaSchema(Schema):
    """Storage quota schema."""

    quota_size = fields.Integer(required=True)
    max_file_size = fields.Integer(required=True)
    notes = SanitizedUnicode(dump_default="")
