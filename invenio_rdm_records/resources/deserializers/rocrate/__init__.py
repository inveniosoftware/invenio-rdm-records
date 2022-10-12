# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RO-Crate deserializer."""

from flask_babelex import lazy_gettext as _
from flask_resources import JSONDeserializer

from ..errors import DeserializerError
from .schema import ROCrateSchema


class ROCrateJSONDeserializer(JSONDeserializer):
    """RO-Crate metadata deserializer."""

    def __init__(self, schema=ROCrateSchema):
        """Deserializer initialization."""
        self.schema = schema

    def deserialize(self, data):
        """Deserialize the RO-Crate payload."""
        data = super().deserialize(data)
        graph = data.get("@graph")
        if not graph:
            raise DeserializerError(
                _("Invalid RO-Crate metadata format, missing '@graph' key.")
            )

        dataset = self._dereference(graph)
        metadata = self.schema().load(dataset)
        return {"metadata": metadata}

    @staticmethod
    def _dereference(data: list):
        entities = {}
        for item in data:
            if "@id" in item:
                entities[item["@id"]] = item
            item.pop("@reverse", None)

        dataset = entities.pop("./")

        def _walk(node):
            if isinstance(node, dict):
                for key in list(node.keys()):
                    value = node[key]
                    if key == "@id" and value in entities:
                        node.update(entities[value])
                    if isinstance(value, (list, dict)):
                        _walk(value)
            elif isinstance(node, list):
                for item in node:
                    _walk(item)

        for value in entities.values():
            _walk(value)
        _walk(dataset)

        return dataset
