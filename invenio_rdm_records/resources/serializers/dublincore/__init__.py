# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dublin Core Serializers for Invenio RDM Records."""

from dcxml import simpledc
from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer, SimpleSerializer

from ....contrib.journal.processors import JournalDublinCoreDumper
from ....contrib.meeting.processors import MeetingDublinCoreDumper
from .schema import DublinCoreSchema


class DublinCoreJSONSerializer(MarshmallowSerializer):
    """Marshmallow based Dublin Core serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=DublinCoreSchema,
            list_schema_cls=BaseListSchema,
            schema_kwargs={
                # processors order matters
                "dumpers": [JournalDublinCoreDumper(), MeetingDublinCoreDumper()]
            },
            **options,
        )


class DublinCoreXMLSerializer(MarshmallowSerializer):
    """Marshmallow based Dublin Core serializer for records.

    Note: This serializer is not suitable for serializing large number of
    records.
    """

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=SimpleSerializer,
            object_schema_cls=DublinCoreSchema,
            list_schema_cls=BaseListSchema,
            schema_kwargs={
                "dumpers": [JournalDublinCoreDumper(), MeetingDublinCoreDumper()]
            },
            encoder=simpledc.tostring,
            **options,
        )
