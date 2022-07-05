# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom Fields for InvenioRDM."""

from .base import BaseCF


class TextCF(BaseCF):
    """Text custom field."""

    def __init__(self, name, exact_match=False):
        """Constructor."""
        self._exact_match = exact_match
        super().__init__(name)

    def mapping_type(self):
        """Return the mapping type."""
        return "text"

    def validate(self):
        """Validate the custom field."""
        return True
