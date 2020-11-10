# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Contributor Role Vocabulary."""

from .vocabulary import Vocabulary


class AccessRightVocabulary(Vocabulary):
    """Encapsulates all access right choices.

    NOTE: Perhaps a stretch of Vocabulary, but very useful.
    """

    key_field = 'access_right'

    @property
    def readable_key(self):
        """Returns the key to readable values for this vocabulary."""
        return 'access_right_name'

    @property
    def vocabulary_name(self):
        """Returns the human readable name for this vocabulary."""
        return 'access right'

    def get_entry_by_dict(self, dict_key):
        """Returns a vocabulary entry as an OrderedDict."""
        if isinstance(dict_key, str):
            dict_key = {self.key_field: dict_key}
        return super().get_entry_by_dict(dict_key)
