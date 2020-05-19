# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Contributor Role Vocabulary."""

from .vocabulary import Vocabulary


class TitleTypeVocabulary(Vocabulary):
    """Encapsulates all title type vocabulary data."""

    @property
    def readable_key(self):
        """Returns the key to readable values for this vocabulary."""
        return 'type_name'

    @property
    def vocabulary_name(self):
        """Returns the human readable name for this vocabulary."""
        return 'title type'

    def key(self, row):
        """Returns the primary key of the row.

        row: dict-like
        returns: serializable
        """
        return row.get('type')
