# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Communities fixture module."""

from .fixture import FixtureMixin


class CommunitiesFixture(FixtureMixin):
    """Communities fixture."""

    def __init__(
        self, search_paths, filename, create_record_func, logo_path=None, delay=True
    ):
        """Initialize the communities fixture."""
        super().__init__(search_paths, filename, create_record_func, delay)
        self.logo_path = logo_path

    def create(self, entry):
        """Load a single community."""
        logo = entry.pop("logo", None)
        feature = entry.pop("feature", False)
        logo_file_path = None
        if logo:
            logo_file_path = str(self.logo_path / logo)

        self.create_record(entry, logo_path=logo_file_path, feature=feature)
