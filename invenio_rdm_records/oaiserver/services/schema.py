# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
# Copyright (C) 2024 KTH Royal Institute of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OAI-PMH API schemas."""

from invenio_i18n import lazy_gettext as _
from marshmallow import EXCLUDE, Schema, fields, validate
from marshmallow_utils.fields import SanitizedUnicode


class OAIPMHMetadataFormat(Schema):
    """Marshmallow schema for OAI-PMH metadata format."""

    id = fields.Str(metadata={"read_only": True})
    schema = fields.URL(metadata={"read_only": True})
    namespace = fields.URL(metadata={"read_only": True})


class OAIPMHSetSchema(Schema):
    """Marshmallow schema for OAI-PMH set."""

    description = SanitizedUnicode(load_default=None, dump_default=None)
    name = SanitizedUnicode(required=True, validate=validate.Length(min=1, max=255))
    search_pattern = SanitizedUnicode(
        required=True, metadata={"title": _("Search pattern")}
    )
    spec = SanitizedUnicode(
        required=True,
        metadata={"create_only": True},
        validate=validate.Length(min=1, max=255),
    )
    created = fields.DateTime(dump_only=True)
    updated = fields.DateTime(dump_only=True)
    system_created = fields.Boolean(dump_only=True)
    id = fields.Int(dump_only=True)

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE
        ordered = True
