# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Northwestern University.
# Copyright (C) 2024-2025 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Signposting serializers."""

from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer, SimpleSerializer

from .schema import FAIRSignpostingProfileLvl2Schema, LandingPageLvl1Schema


class FAIRSignpostingProfileLvl1Serializer(MarshmallowSerializer):
    """FAIR Signposting Profile level 1 serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=SimpleSerializer,
            object_schema_cls=LandingPageLvl1Schema,
            list_schema_cls=BaseListSchema,
            encoder=self.fair_signposting_tostring,
        )

    @classmethod
    def fair_signposting_tostring(cls, record):
        """Stringify a FAIR Signposting record."""
        links = []
        for rel, values in record.items():
            for value in values:
                link = f'<{value["href"]}> ; rel="{rel}"'
                if "type" in value:
                    link += f' ; type="{value["type"]}"'
                links.append(link)
        return " , ".join(links)


class FAIRSignpostingProfileLvl2Serializer(MarshmallowSerializer):
    """FAIR Signposting Profile level 2 serializer."""

    def __init__(self):
        """Initialise Serializer."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=FAIRSignpostingProfileLvl2Schema,
            list_schema_cls=BaseListSchema,
        )
