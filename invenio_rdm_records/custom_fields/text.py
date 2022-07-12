# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom Fields for InvenioRDM."""

from marshmallow_utils.fields import SanitizedUnicode

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
        """Marshmallow schema for vocabulary custom fields."""
        return SanitizedUnicode()


class KeywordCF(TextCF):
    """Keyword custom field"""

    def mapping(self):
        """Return mapping"""
        return {"type": "keyword"}

