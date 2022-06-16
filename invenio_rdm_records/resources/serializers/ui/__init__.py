# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record response serializers."""

from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer

from .schema import UIRecordSchema


class UIJSONSerializer(MarshmallowSerializer):
    """UI JSON serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=UIRecordSchema,
            list_schema_cls=BaseListSchema,
            schema_context={"object_key": "ui"},
        )
