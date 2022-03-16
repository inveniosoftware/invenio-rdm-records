# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OAI-PMH API schemas."""

from marshmallow import Schema, fields, validate
from marshmallow_utils.fields import SanitizedUnicode


class OAIPMHMetadataFormat(Schema):
    """Marshmallow schema for OAI-PMH metadata format."""

    id = fields.Str(metadata={'read_only': True})
    schema = fields.URL(metadata={'read_only': True})
    namespace = fields.URL(metadata={'read_only': True})


class OAIPMHSetSchema(Schema):
    """Marshmallow schema for OAI-PMH set."""

    description = SanitizedUnicode(load_default=None, dump_default=None)
    name = SanitizedUnicode(
        required=True, validate=validate.Length(min=1, max=255)
    )
    search_pattern = SanitizedUnicode(required=True)
    spec = SanitizedUnicode(
        required=True, validate=validate.Length(min=1, max=255)
    )
    created = fields.DateTime(metadata={'read_only': True})
    updated = fields.DateTime(metadata={'read_only': True})
    id = fields.Int(metadata={'read_only': True})
