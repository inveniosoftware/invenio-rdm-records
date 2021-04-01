# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from marshmallow import Schema, fields, EXCLUDE


class ExternalPIDsSchema(Schema):
    """External PIDs schema."""

    class Meta:

        unknown = EXCLUDE

    identifier = fields.Str(required=True)
    provider = fields.Str(required=True)
    client = fields.Str()
