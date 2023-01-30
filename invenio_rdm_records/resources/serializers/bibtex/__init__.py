# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""BibTex Serializer for Invenio RDM Records."""

from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import SimpleSerializer

from .schema import BibTexSchema


class BibtexSerializer(MarshmallowSerializer):
    """Marshmallow based BibTex serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=SimpleSerializer,
            object_schema_cls=BibTexSchema,
            list_schema_cls=BaseListSchema,
            encoder=self.bibtex_tostring,
        )

    @classmethod
    def bibtex_tostring(cls, record):
        """Stringify a BibTex record."""
        return record
