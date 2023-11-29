# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""CFF serializer."""


from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers.yaml import YAMLFormatter

from .schema import CFFSchema


class CFFSerializer(MarshmallowSerializer):
    """Marshmallow based CFF serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=YAMLFormatter,
            object_schema_cls=CFFSchema,
            list_schema_cls=BaseListSchema,
            **options
        )
