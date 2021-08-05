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


class OptionsSelector:
    """Generic helper to select and validate facet/sort options."""

    def __init__(self, available_options, selected_options):
        """Initialize selector."""
        # Ensure all selected options are availabe.
        for o in selected_options:
            assert o in available_options, \
                    f"Selected option '{o}' is undefined."

        self.available_options = available_options
        self.selected_options = selected_options

    def __iter__(self):
        """Iterate over options to produce RSK options."""
        for o in self.selected_options:
            yield self.map_option(o, self.available_options[o])

    def map_option(self, key, option):
        """Map an option."""
        # This interface is used in Invenio-App-RDM.
        return (key, option)


class SortOptionsSelector(OptionsSelector):
    """Sort options for the search configuration."""

    def __init__(self, available_options, selected_options, default=None,
                 default_no_query=None):
        """Initialize sort options."""
        super().__init__(available_options, selected_options)

        self.default = selected_options[0] if default is None else default
        self.default_no_query = selected_options[1] \
            if default_no_query is None else default_no_query

        assert self.default in self.available_options, \
            f"Default sort with query {self.default} is undefined."
        assert self.default_no_query in self.available_options, \
            f"Default sort without query {self.default_no_query} is undefined."


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
