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
        return etree.tostring(
            dumps_etree(json),
            pretty_print=True,
            encoding="utf-8",
        ).decode("utf-8")

    def serialize_object_list(self, records, **kwargs):
        """Serialize a list of records."""
        return "\n".join(
            [self.serialize_object(rec, **kwargs) for rec in records["hits"]["hits"]]
        )
