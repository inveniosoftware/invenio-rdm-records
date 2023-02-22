# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite Serializers for Invenio RDM Records."""
from datacite import schema43
from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer, XMLSerializer

from .schema import DataCite43Schema


class DataCite43JSONSerializer(MarshmallowSerializer):
    """Marshmallow based DataCite serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=DataCite43Schema,
            list_schema_cls=BaseListSchema,
            **options
        )


class DataCite43XMLSerializer(MarshmallowSerializer):
    """JSON based DataCite XML serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=XMLSerializer,
            object_schema_cls=DataCite43Schema,
            list_schema_cls=BaseListSchema,
            string_encoder=schema43.tostring,
        )
