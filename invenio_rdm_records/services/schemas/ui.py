# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from invenio_records_rest.schemas.fields import SanitizedUnicode
from marshmallow import INCLUDE, Schema, post_dump
from marshmallow_utils.fields import LocalizedEDTFDateString

class UISchema(Schema):
    """UI config schema."""

    publication_date_l10n = LocalizedEDTFDateString(
        attribute="publication_date")
