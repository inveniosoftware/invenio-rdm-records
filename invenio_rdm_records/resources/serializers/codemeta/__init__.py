# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Codemeta serializer."""

from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer

from invenio_rdm_records.contrib.codemeta.processors import CodemetaDumper

from .schema import CodemetaSchema


class CodemetaSerializer(MarshmallowSerializer):
    """Marshmallow based DataCite serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=CodemetaSchema,
            list_schema_cls=BaseListSchema,
            schema_kwargs={"dumpers": [CodemetaDumper()]},  # Order matters
            **options,
        )
