# -*- coding: utf-8 -*-
#
# Copyright (C) 2018-2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Search app configuration helper."""


# NOTE: It would be best to try to better harmonize these classes together with
# the ones in Invenio-App-RDM used for the frontend and try to lower the number
# of classes used for passing config around.

from invenio_search_ui.searchconfig import SortOptionsSelector, OptionsSelector


class SearchConfig:
    """Search endpoint configuration."""

    def __init__(self, config, sort=None, facets=None):
        """Initialize search config."""
        config = config or {}
        self._sort = []
        self._facets = []

        if 'sort' in config:
            self._sort = SortOptionsSelector(
                sort,
                config['sort'],
                default=config.get('sort_default'),
                default_no_query=config.get('sort_default_no_query')
            )
        if 'facets' in config:
            self._facets = OptionsSelector(facets, config.get('facets'))

    @property
    def sort_options(self):
        """Get sort options for search."""
        return {k: v for (k, v) in self._sort}

    @property
    def sort_default(self):
        """Get default sort method for search."""
        return self._sort.default if self._sort else None

    @property
    def sort_default_no_query(self):
        """Get default sort method without query for search."""
        return self._sort.default_no_query if self._sort else None

    @property
    def facets(self):
        """Get facets for search."""
        return {k: v['facet'] for (k, v) in self._facets}
