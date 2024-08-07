# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Schemaorg Serializers for Invenio RDM Records."""

from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer

from ....contrib.journal.processors import JournalSchemaorgDumper
from .schema import SchemaorgSchema


class SchemaorgJSONLDSerializer(MarshmallowSerializer):
    """Marshmallow based Schemaorg serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=SchemaorgSchema,
            list_schema_cls=BaseListSchema,
            schema_kwargs={"dumpers": [JournalSchemaorgDumper()]},  # Order matters
            **options,
        )
