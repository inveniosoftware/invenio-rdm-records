# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""CFF serializer."""

import yaml
from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import SimpleSerializer

from .schema import CFFSchema


class CFFSerializer(MarshmallowSerializer):
    """Marshmallow based CFF serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        encoder = options.get("encoder", yaml.dump)
        super().__init__(
            format_serializer_cls=SimpleSerializer,
            object_schema_cls=CFFSchema,
            list_schema_cls=BaseListSchema,
            encoder=encoder,
            **options,
        )
