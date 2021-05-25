# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 data-futures.org.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""IIIF Presentation API Serializers for Invenio RDM Records."""

from flask_resources.serializers import MarshmallowJSONSerializer
from .schema import IIIFPresiSchema


class IIIFPresiSerializer(MarshmallowJSONSerializer):
    """Marshmallow based IIIF Presentation API serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(schema_cls=IIIFPresiSchema, **options)

    def dump_one(self, obj):
        """Return as basic manifest suitable for bootstrapping a viewer."""
        return self._schema_cls().dump(obj)
