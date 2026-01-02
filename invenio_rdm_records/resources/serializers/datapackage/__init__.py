# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Open Knowledge Foundation
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Data Package Serializers for Invenio RDM Records."""

from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer

from .schema import DataPackageSchema


class DataPackageSerializer(MarshmallowSerializer):
    """Marshmallow based Data Package serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=DataPackageSchema,
            list_schema_cls=BaseListSchema,
            **options
        )
