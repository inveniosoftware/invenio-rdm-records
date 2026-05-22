# SPDX-FileCopyrightText: 2020-2021 CERN.
# SPDX-FileCopyrightText: 2020-2021 Northwestern University.
# SPDX-License-Identifier: MIT

"""RDM record schemas."""

from marshmallow import Schema
from marshmallow_utils.fields import SanitizedUnicode


class PIDSchema(Schema):
    """PIDs schema."""

    identifier = SanitizedUnicode(required=True)
    provider = SanitizedUnicode(required=True)
    client = SanitizedUnicode()
