# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from invenio_records_rest.schemas.fields import DateString, SanitizedUnicode
from marshmallow import INCLUDE, Schema, fields, validate


class StatsSchemaV1(Schema):
    """Files metadata schema."""

    views = fields.Int()
    downloads = fields.Int()
