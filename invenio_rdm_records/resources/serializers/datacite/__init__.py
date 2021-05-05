# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite Serializers for Invenio RDM Records."""

from flask_resources.serializers import MarshmallowJSONSerializer

from .schema import DataCite43Schema


class DataCite43JSONSerializer(MarshmallowJSONSerializer):
    """Marshmallow based DataCite serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(schema_cls=DataCite43Schema, **options)

    def dump_one(self, obj):
        """Dump the object with extra information."""
        return self._schema_cls().dump(obj)
