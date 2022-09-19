# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dublin Core Serializers for Invenio RDM Records."""

from dcxml import simpledc
from flask_resources.serializers import MarshmallowJSONSerializer, SerializerMixin

from .schema import DublinCoreSchema


class DublinCoreJSONSerializer(MarshmallowJSONSerializer):
    """Marshmallow based Dublin Core serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(schema_cls=DublinCoreSchema, **options)


class DublinCoreXMLSerializer(SerializerMixin):
    """Marshmallow based Dublin Core serializer for records.

    Note: This serializer is not suitable for serializing large number of
    records.
    """

    def __init__(self, **options):
        """Constructor."""
        self._schema_cls = DublinCoreSchema

    def serialize_object_xml(self, obj):
        """Serialize a single record and persistent identifier to etree.

        :param obj: Record instance
        """
        json = self._schema_cls().dump(obj)
        return simpledc.dump_etree(json)

    def serialize_object(self, obj):
        """Serialize a single record and persistent identifier.

        :param obj: Record instance
        """
        json = self._schema_cls().dump(obj)
        return simpledc.tostring(json)

    def serialize_object_list(self, obj_list):
        """Serialize a list of records.

        :param obj_list: List of record instances
        """
        records = obj_list.get("hits", {}).get("hits", [])
        json_list = self._schema_cls().dump(records, many=True)
        # TODO: multiple records should be wrapped in a single root tag.
        return "\n".join(simpledc.tostring(json) for json in json_list)
