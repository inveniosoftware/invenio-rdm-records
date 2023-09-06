# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""MARCXML Serializer for Invenio RDM Records."""

from dojson.contrib.to_marc21.utils import dumps_etree
from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import SimpleSerializer
from lxml import etree

from ....contrib.imprint.processors import ImprintMarcXMLDumper
from ....contrib.journal.processors import JournalMarcXMLDumper
from .schema import MARCXMLSchema


class MARCXMLSerializer(MarshmallowSerializer):
    """Marshmallow based MARCXML serializer for records.

    Note: This serializer is not suitable for serializing large number of
    records.
    """

    def __init__(self, **options):
        """Constructor."""
        super().__init__(
            format_serializer_cls=SimpleSerializer,
            object_schema_cls=MARCXMLSchema,
            list_schema_cls=BaseListSchema,
            schema_kwargs={
                "dumpers": [JournalMarcXMLDumper(), ImprintMarcXMLDumper()]
            },  # Order matters
            encoder=self.marcxml_tostring,
        )

    @classmethod
    def marcxml_tostring(cls, record):
        """Stringify a MarcXML record."""
        return etree.tostring(
            dumps_etree(record),
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8",
        ).decode("utf-8")
