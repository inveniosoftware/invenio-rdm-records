# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Schemas related to record deletion status and tombstones."""

from marshmallow import Schema, fields
from marshmallow_utils.fields import SanitizedUnicode


class QuotaSchema(Schema):
    """Storage quota schema."""

    quota_size = fields.Number(required=True)
    max_file_size = fields.Number(required=True)
    notes = SanitizedUnicode(default="")
