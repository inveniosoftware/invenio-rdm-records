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

from invenio_rdm_records.contrib.journal.custom_fields import JournalDublinCoreDumper
from invenio_rdm_records.contrib.meeting.custom_fields import MeetingDublinCoreDumper

from .schema import DublinCoreSchema

# Order matters
dublincore_dumpers = [JournalDublinCoreDumper(), MeetingDublinCoreDumper()]


class DublinCoreJSONSerializer(MarshmallowSerializer):
    """Marshmallow based Dublin Core serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=DublinCoreSchema,
            list_schema_cls=BaseListSchema,
            schema_kwargs={"dumpers": dublincore_dumpers},
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
            schema_kwargs={"dumpers": dublincore_dumpers},
            encoder=simpledc.tostring,
            **options,
        )
