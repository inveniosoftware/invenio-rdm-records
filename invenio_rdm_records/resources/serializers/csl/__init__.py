# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""CSL JSON Serializers for Invenio RDM Records."""

from flask_resources.serializers import MarshmallowJSONSerializer

from .schema import CSLJSONSchema


class CSLJSONSerializer(MarshmallowJSONSerializer):
    """Marshmallow based CSL JSON serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(schema_cls=CSLJSONSchema, **options)
