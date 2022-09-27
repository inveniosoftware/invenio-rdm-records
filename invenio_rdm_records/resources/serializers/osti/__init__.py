# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 PNNL.
# Copyright (C) 2022 BNL.

# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OSTI Serializers for Invenio RDM Records."""
from flask_resources.serializers import MarshmallowJSONSerializer
from .schema import OSTISchema


class OSTIJSONSerializer(MarshmallowJSONSerializer):
    """Marshmallow based OSTI serializer for records."""

    def __init__(self, **options):
        """Constructor."""
        super().__init__(schema_cls=OSTISchema, **options)


