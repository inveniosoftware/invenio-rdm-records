# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Data fixtures module."""

import yaml


class FixtureMixin:
    """Fixture loading mixin."""

    def __init__(self, search_paths, filename, create_record_func=None, delay=True):
        """Initialize the fixture."""
        self._search_paths = search_paths
        self._filename = filename
        self.create_record_func = create_record_func
        self._delay = delay

    def load(self):
        """Load the fixture.

        The first file matching the filename found in self._search_paths is
        chosen.
        """
        for path in self._search_paths:
            filepath = path / self._filename

            # Providing a yaml file is optional
            if not filepath.exists():
                continue

            with open(filepath) as fp:
                data = yaml.safe_load(fp) or []
                for item in data:
                    self.create(item)

            break

    def read(self):
        """Read the entries.

        The first file matching the filename found in self._search_paths is
        chosen.
        """
        for path in self._search_paths:
            filepath = path / self._filename

            # Providing a yaml file is optional
            if not filepath.exists():
                continue

            with open(filepath) as fp:
                return list(yaml.safe_load(fp)) or []

    def create_record(self, *args, **kwargs):
        """Creates record."""
        if self._delay:
            self.create_record_func.delay(*args, **kwargs)
        else:
            self.create_record_func(*args, **kwargs)
