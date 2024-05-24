# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Signposting serializers."""

from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer

from .schema import FAIRSignpostingProfileLvl2Schema


class FAIRSignpostingProfileLvl2Serializer(MarshmallowSerializer):
    """FAIR Signposting Profile level 2 serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=FAIRSignpostingProfileLvl2Schema,
            list_schema_cls=BaseListSchema,
        )
