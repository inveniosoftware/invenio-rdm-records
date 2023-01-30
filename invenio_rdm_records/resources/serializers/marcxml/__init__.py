# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""MARCXML Serializer for Invenio RDM Records."""


import traceback
from copy import deepcopy

from dojson.contrib.to_marc21.utils import dumps_etree
from flask_resources.serializers import SerializerMixin
from lxml import etree

from .schema import MARCXMLSchema


class MARCXMLSerializer(SerializerMixin):
    """Marshmallow based MARCXML serializer for records.

    Note: This serializer is not suitable for serializing large number of
    records.
    """

    def __init__(self, **options):
        """Constructor."""
        self._schema_cls = MARCXMLSchema

    def serialize_object(self, obj):
        """Serialize a single record and persistent identifier to etree.

        :param obj: Record instance
        """
        json = self._schema_cls().dump(obj)

        def changeKeysToTags(dict):
            """Changes the key name to the corresponding MARCXML tag (number)."""
            # [!] The string in the first array corresponds to the tag[0:4] + ind1[4] + ind2[5]
            # [!] The first string needs to be length *5* (this is to do with the dojson parser)
            # [!] The second string corresponds to the subfield code

            # Example: "creators" : ["100a ", "a"]

            #   <datafield tag="100" ind1="a" ind2=" ">
            #       <subfield code="a">Tarocco, Nicola</subfield>
            #   </datafield>

            # To add support for more tags, use the corresponding codes from here
            # https://scoap3.org/scoap3-repository/marcxml/

            changes = {
                "contributors": ["700a ", "u"],  # Abstract
                "titles": ["245a ", "a"],  # Title
                "creators": ["100a ", "a"],  # First author
                "identifiers": ["024  ", "a"],  # DOI
                "relations": ["856 2", "a"],  # Related Ressource
                "rights": ["540  ", "a"],  # License
                "dates": [
                    "260c ",
                    "c",
                ],  # Publication Information - Date of Publication
                "subjects": ["653  ", "a"],  # Keywords
                "descriptions": ["520  ", "a"],  # Abstract
                "publishers": [
                    "260b ",
                    "a",
                ],  # Publication Information - Publisher Name
                "types": ["901  ", "u"],  # Local Implementation
                "sources": ["246i ", "x"],  # Source
                "coverage": ["510  ", "a"],  # Location
                "formats": ["520 1", "a"],  # Abstract
                "parent_id": ["024 1", "a"],  # ID
                "community_id": ["024 2", "a"],  # ID
                "last_updated": [
                    "260ca",
                    "c",
                ],  # Publication Information - Date of Publication
                "sizes": ["520 2", "a"],  # Abstract
                "version": ["024 3", "a"],  # ID
                "funding": ["856 1", "a"],  # Related Ressource
            }

            dict_copy = deepcopy(dict)
            for key in dict_copy:
                if key in changes:
                    dict[changes[key][0]] = {changes[key][1]: dict.pop(key)}

            return dict

        json = changeKeysToTags(json)
        return etree.tostring(dumps_etree(json))
