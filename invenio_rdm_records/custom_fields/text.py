# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom Fields for InvenioRDM."""

from marshmallow import fields
from marshmallow_utils.fields import SanitizedUnicode
from invenio_vocabularies.services.schema import VocabularySchema

from .base import BaseCF


class TextCF(BaseCF):
    """Text custom field."""

    def __init__(self, name, use_as_filter=False):
        """Constructor."""
        self.use_as_filter = use_as_filter
        super().__init__(name)

    @property
    def mapping(self):
        """Return the mapping."""
        _mapping = {"type": "text"}
        if self.use_as_filter:
            _mapping["fields"] = {"keyword": {"type": "keyword"}}
        return _mapping

    def schema(self):
        """Validate the custom field."""
        return SanitizedUnicode()


class KeywordCF(TextCF):
    """Keyword custom field"""

    def mapping(self):
        """Return mapping"""
        return {"type": "keyword"}


class VocabularyCF(BaseCF):
    """Vocabulary custom field.

    Supporting common vocabulary structure.
    """

    type = "vocabulary"

    def __init__(self, name, vocabulary_id):
        """Constructor."""
        self.vocabulary_id = vocabulary_id
        super().__init__(name)

    @property
    def mapping(self):
        """Return the mapping."""
        _mapping = {
            "type": "object",
            "properties": {
                "@v": {"type": "keyword"},
                "id": {"type": "keyword"},
                "title": {"type": "object", "dynamic": True},
            },
        }

        return _mapping

    def schema(self):
        """Validate the custom field."""
        return fields.Mapping()

    def options(self):
        """."""
        return [
            {"text": "Zacharias Zacharodimos", "value": "zzacharo"},
            {"text": "Pablo Panero", "value": "ppanero"},
        ]
