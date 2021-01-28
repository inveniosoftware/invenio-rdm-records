# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Data fixtures module."""

from os.path import dirname, join

from .vocabularies import VocabulariesFixture


class SearchPath:
    """Basic class that helps with finding a specific file name.

    TODO: This class is meant to be further developed from this very basic
    view.
    """

    def __init__(self, root):
        """Initialize the search path."""
        self._root = root

    def path(self, file_path):
        """Lookup a specific filename path in the search directories."""
        return join(self._root, file_path)


class FixturesEngine:
    """Basic fixtures engine.

    TODO: This engine is meant to be heavily expanded to allow for loading all
    types of data from vocabularies, access control and records.
    """

    def __init__(self, identity):
        """Initialize the class."""
        self._identity = identity

    @property
    def data_dir(self):
        """Initialize the class."""
        return join(dirname(__file__), 'data')

    def run(self):
        """Run the fixture loading."""
        VocabulariesFixture(
            self._identity,
            SearchPath(self.data_dir),
            'vocabularies.yaml',
        ).load()
