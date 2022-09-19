# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 data-futures.
# Copyright (C) 2022 Universität Hamburg.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""IIIF Presentation API Schema for Invenio RDM Records."""

from flask_resources.serializers import MarshmallowJSONSerializer

from .schema import (
    IIIFCanvasV2Schema,
    IIIFInfoV2Schema,
    IIIFManifestV2Schema,
    IIIFSequenceV2Schema,
)


class IIIFInfoV2JSONSerializer(MarshmallowJSONSerializer):
    """Marshmallow based IIIF info serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(schema_cls=IIIFInfoV2Schema, **options)


class IIIFSequenceV2JSONSerializer(MarshmallowJSONSerializer):
    """Marshmallow based IIIF sequence serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(schema_cls=IIIFSequenceV2Schema, **options)


class IIIFCanvasV2JSONSerializer(MarshmallowJSONSerializer):
    """Marshmallow based IIIF canvas serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(schema_cls=IIIFCanvasV2Schema, **options)


class IIIFManifestV2JSONSerializer(MarshmallowJSONSerializer):
    """Marshmallow based IIIF Presi serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(schema_cls=IIIFManifestV2Schema, **options)
