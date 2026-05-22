# SPDX-FileCopyrightText: 2023-2024 CERN
# SPDX-License-Identifier: MIT

"""GeoJSON Serializers for Invenio RDM Records."""

from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer

from .schema import GeoJSONSchema


class GeoJSONSerializer(MarshmallowSerializer):
    """Marshmallow based GeoJSON serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=GeoJSONSchema,
            list_schema_cls=BaseListSchema,
            **options,
        )
