# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2025 CERN.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite Serializers for Invenio RDM Records."""

from datacite import schema43, schema45
from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer, SimpleSerializer

from ....contrib.journal.processors import JournalDataciteDumper
from .schema import DataCite43Schema, DataCite45Schema


class DataCite43JSONSerializer(MarshmallowSerializer):
    """Marshmallow based DataCite schema v4.3 serializer for records."""

    def __init__(self, is_parent=False, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=DataCite43Schema,
            list_schema_cls=BaseListSchema,
            schema_kwargs={
                "dumpers": [JournalDataciteDumper()],  # Order matters
                "is_parent": is_parent,
            },
            **options,
        )


class DataCite43XMLSerializer(MarshmallowSerializer):
    """JSON based DataCite schema v4.3 XML serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        encoder = options.get("encoder", schema43.tostring)
        super().__init__(
            format_serializer_cls=SimpleSerializer,
            object_schema_cls=DataCite43Schema,
            list_schema_cls=BaseListSchema,
            schema_kwargs={"dumpers": [JournalDataciteDumper()]},  # Order matters
            encoder=encoder,
        )


class DataCite45JSONSerializer(MarshmallowSerializer):
    """Marshmallow based DataCite schema v4.5 JSON serializer for records."""

    def __init__(self, is_parent=False, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=DataCite45Schema,
            list_schema_cls=BaseListSchema,
            schema_kwargs={
                "dumpers": [JournalDataciteDumper()],
                "is_parent": is_parent,
            },  # Order matters
            **options,
        )


class DataCite45XMLSerializer(MarshmallowSerializer):
    """JSON based DataCite schema v4.5 XML serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        encoder = options.get("encoder", schema45.tostring)
        super().__init__(
            format_serializer_cls=SimpleSerializer,
            object_schema_cls=DataCite45Schema,
            list_schema_cls=BaseListSchema,
            schema_kwargs={"dumpers": [JournalDataciteDumper()]},  # Order matters
            encoder=encoder,
        )
