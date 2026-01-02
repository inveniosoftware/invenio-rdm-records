# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2021 data-futures.
# Copyright (C) 2022 Universität Hamburg.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""IIIF Presentation API Schema for Invenio RDM Records."""

from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer

from .schema import (
    IIIFCanvasV2Schema,
    IIIFInfoV2Schema,
    IIIFManifestV2Schema,
    IIIFSequenceV2Schema,
)


class IIIFInfoV2JSONSerializer(MarshmallowSerializer):
    """Marshmallow based IIIF info serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=IIIFInfoV2Schema,
            list_schema_cls=BaseListSchema,
            **options,
        )


class IIIFSequenceV2JSONSerializer(MarshmallowSerializer):
    """Marshmallow based IIIF sequence serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=IIIFSequenceV2Schema,
            list_schema_cls=BaseListSchema,
            **options,
        )


class IIIFCanvasV2JSONSerializer(MarshmallowSerializer):
    """Marshmallow based IIIF canvas serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=IIIFCanvasV2Schema,
            list_schema_cls=BaseListSchema,
            **options,
        )


class IIIFManifestV2JSONSerializer(MarshmallowSerializer):
    """Marshmallow based IIIF Presi serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=IIIFManifestV2Schema,
            list_schema_cls=BaseListSchema,
            **options,
        )
