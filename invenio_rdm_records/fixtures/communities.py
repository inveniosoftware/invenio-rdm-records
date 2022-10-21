# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Communities fixture module."""

from pathlib import Path

from invenio_communities.fixtures.tasks import create_demo_community

from .fixture import FixtureMixin


class CommunitiesFixture(FixtureMixin):
    """Communities fixture."""

    def __init__(self, search_paths, filename, logo_path):
        """Initialize the communities fixture."""
        super().__init__(search_paths, filename)
        self.logo_path = logo_path

    def create(self, entry):
        """Load a single community."""
        logo = entry.pop("logo", None)

        if logo:
            logo_file_path = self.logo_path / logo
            create_demo_community(entry, logo_file_path)
        else:
            create_demo_community(entry)
