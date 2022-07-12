# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom Fields for InvenioRDM."""

from .text import KeywordCF, TextCF
from .vocabulary import VocabularyCF

__all__ = (
    "KeywordCF",
    "TextCF",
    "VocabularyCF",
)
