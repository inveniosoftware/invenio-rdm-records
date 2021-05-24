# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2021 CERN.
# Copyright (C) 2019-2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Data fixtures module."""

from pathlib import Path

from .users import UsersFixture
from .vocabularies import VocabulariesFixture


class FixturesEngine:
    """Basic fixtures engine.

    TODO: This engine is meant to be heavily expanded to allow for loading all
    types of data from vocabularies, access control and records.
    """

    def __init__(self, identity):
        """Initialize the class."""
        self._identity = identity

    def run(self):
        """Run the fixture loading."""
        dir_ = Path(__file__).parent

        VocabulariesFixture(
            self._identity,
            [Path("./app_data"), dir_ / "data"],
            'vocabularies.yaml',
        ).load()

        UsersFixture(
            [Path("./app_data"), dir_ / "data"],
            'users.yaml',
        ).load()
