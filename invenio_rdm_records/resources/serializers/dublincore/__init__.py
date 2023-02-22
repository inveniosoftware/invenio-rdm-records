# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dublin Core Serializers for Invenio RDM Records."""

from dcxml import simpledc
from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer, SerializerMixin

from .schema import DublinCoreSchema


class DublinCoreJSONSerializer(MarshmallowSerializer):
    """Marshmallow based Dublin Core serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=DublinCoreSchema,
            list_schema_cls=BaseListSchema,
            **options
        )


class DublinCoreXMLSerializer(DublinCoreJSONSerializer):
    """Marshmallow based Dublin Core serializer for records.

    Note: This serializer is not suitable for serializing large number of
    records.
    """

    def serialize_object(self, record, **kwargs):
        """Serialize a single record and persistent identifier.

        :param obj: Record instance
        """
        json = self.dump_obj(record, **kwargs)
        return simpledc.tostring(json)

    def serialize_object_list(self, records, **kwargs):
        """Serialize a list of records."""
        # TODO: multiple records should be wrapped in a single root tag.
        return "\n".join(
            [self.serialize_object(rec, **kwargs) for rec in records["hits"]["hits"]]
        )
