# SPDX-FileCopyrightText: 2024 CERN.
# SPDX-License-Identifier: MIT

"""Query Parser module for InvenioRdmRecords."""

from luqum.tree import Word


def word_internal_notes(node):
    """Rewrite the internal notes."""
    if not node.value.startswith("internal_notes"):
        return node
    return Word(" ")
