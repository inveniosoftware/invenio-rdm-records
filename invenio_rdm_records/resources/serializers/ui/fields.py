# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record response serializers."""

from marshmallow import fields

from invenio_rdm_records.vocabularies import Vocabularies


class VocabularyField(fields.String):
    """Vocabulary field."""

    def __init__(self, vocabulary_name, entry_key=None, **kwargs):
        """Initialize field."""
        self.vocabulary_name = vocabulary_name
        self.entry_key = entry_key
        kwargs.setdefault('dump_only', True)
        super().__init__(**kwargs)

    @property
    def vocabulary(self):
        """Get the vocabulary."""
        return Vocabularies.get_vocabulary(self.vocabulary_name)

    def entry(self, value):
        """Get the vocabulary entry."""
        return self.vocabulary.get_entry_by_dict(value)

    def format(self, value):
        """Get the specific key or object from the vocabulary."""
        entry = self.entry(value)
        return entry[self.entry_key] if self.entry_key else entry

    def _serialize(self, value, attr, obj, **kwargs):
        """Serialize the vocabulary title."""
        return self.format(value)


class VocabularyTitleField(VocabularyField):
    """Vocabulary title field."""

    def entry(self, value):
        """Get the vocabulary title."""
        return self.vocabulary.get_title_by_dict(value)
