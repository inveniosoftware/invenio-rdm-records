# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2022 CERN.
# Copyright (C) 2019-2022 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Data fixtures module."""

from pathlib import Path

from flask import current_app
from invenio_communities.fixtures.tasks import create_demo_community

from .communities import CommunitiesFixture
from .records import RecordsFixture
from .tasks import create_demo_record
from .users import UsersFixture
from .vocabularies import PrioritizedVocabulariesFixtures, VocabulariesFixture


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
        app_data_folder = Path(current_app.instance_path) / "app_data"
        data_folder = dir_ / "data"

        PrioritizedVocabulariesFixtures(
            self._identity,
            app_data_folder=app_data_folder,
            pkg_data_folder=data_folder,
            filename="vocabularies.yaml",
        ).load()

        UsersFixture(
            [app_data_folder, data_folder],
            "users.yaml",
        ).load()

        CommunitiesFixture(
            [app_data_folder, data_folder],
            "communities.yaml",
            create_demo_community,
            app_data_folder / "img",
        ).load()

        RecordsFixture(
            [app_data_folder, data_folder],
            "records.yaml",
            create_demo_record,
        ).load()

    def add_to(self, fixture):
        """Run the fixture loading."""
        dir_ = Path(__file__).parent
        app_data_folder = Path(current_app.instance_path) / "app_data"
        data_folder = dir_ / "data"

        PrioritizedVocabulariesFixtures(
            self._identity,
            app_data_folder=app_data_folder,
            pkg_data_folder=data_folder,
            filename="vocabularies.yaml",
        ).load(reload=fixture)


__all__ = ("FixturesEngine", "PrioritizedVocabulariesFixtures", "VocabulariesFixture")
