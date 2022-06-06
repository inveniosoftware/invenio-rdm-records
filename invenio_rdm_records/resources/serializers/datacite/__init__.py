# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite Serializers for Invenio RDM Records."""
from datacite import schema43
from flask_resources.serializers import MarshmallowJSONSerializer

from .schema import DataCite43Schema


class DataCite43JSONSerializer(MarshmallowJSONSerializer):
    """Marshmallow based DataCite serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(schema_cls=DataCite43Schema, **options)


class DataCite43XMLSerializer(DataCite43JSONSerializer):
    """JSON based DataCite XML serializer for records."""

    def serialize_object(self, record, **kwargs):
        """Serialize a single record."""
        data = self.dump_one(record, **kwargs)
        return schema43.tostring(data)

    def serialize_object_list(self, records, **kwargs):
        """Serialize a list of records."""
        return "\n".join(
            [self.serialize_object(rec, **kwargs) for rec in records["hits"]["hits"]]
        )
