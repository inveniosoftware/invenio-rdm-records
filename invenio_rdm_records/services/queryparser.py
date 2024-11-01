# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Query Parser module for InvenioRdmRecords."""
from luqum.tree import Word


def word_internal_notes(node):
    """Rewrite the internal notes."""
    if not node.value.startswith("internal_notes"):
        return node
    return Word(" ")
