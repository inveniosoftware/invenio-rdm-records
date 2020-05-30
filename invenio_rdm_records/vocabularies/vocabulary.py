# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Vocabulary."""

import csv
from collections import OrderedDict, defaultdict

from flask_babelex import lazy_gettext as _


def hierarchized_rows(dict_reader):
    """Yields filled OrderedDict rows according to csv hierarchy.

    Idea is to have the csv rows:

    fooA, barA-1, bazA-1
        , barA-2, bazA-2
    fooB, barB-1, bazB-1
        ,       , bazB-2

    map to these rows

    fooA, barA-1, bazA-1
    fooA, barA-2, bazA-2
    fooB, barB-1, bazB-1
    fooB, barB-1, bazB-2

    This makes it easy for subject matter experts to fill the csv in
    their spreadsheet software, while also allowing hierarchy of data
    a-la yaml and extensibility for other conversions or data down the road.
    """
    prev_row = defaultdict(lambda: "")

    for row in dict_reader:  # row is an OrderedDict in fieldnames order
        current_row = row
        for field in row:
            if not current_row[field]:
                current_row[field] = prev_row[field]
            else:
                break
        prev_row = current_row
        yield current_row


class Vocabulary(object):
    """Abstracts common vocabulary functionality."""

    def __init__(self, path):
        """Constructor."""
        self.path = path
        self._load_data()

    @property
    def readable_key(self):
        """Returns the key to readable values for this vocabulary."""
        raise NotImplementedError()

    @property
    def vocabulary_name(self):
        """Returns the human readable name for this vocabulary."""
        raise NotImplementedError()

    def key(self, row):
        """Returns the primary key of the row.

        row: dict-like
        returns: serializable
        """
        raise NotImplementedError()

    def _load_data(self):
        """Sets self.data with the filled rows."""
        with open(self.path) as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            # NOTE: We use an OrderedDict to preserve on file row order
            self.data = OrderedDict([
                # NOTE: unfilled cells return '' (empty string)
                (self.key(row), row)
                for row in hierarchized_rows(reader)
            ])

    def get_entry_by_dict(self, dict_key):
        """Returns a vocabulary entry as an OrderedDict."""
        return self.data.get(self.key(dict_key))

    def get_title_by_dict(self, dict_key):
        """Returns the vocabulary entry's human readable name."""
        entry = self.get_entry_by_dict(dict_key)

        # NOTE: translations could also be done via the CSV file directly
        return _(entry.get(self.readable_key))

    def get_invalid(self, dict_key):
        """Returns the error message for the given dict key."""
        # TODO: Revisit with deposit to return targeted error message
        choices = set(self.data.keys())
        _input = self.key(dict_key)

        return _(
            'Invalid {vocabulary_name}. {input} not one of {choices}.'.format(
                vocabulary_name=self.vocabulary_name,
                input=_input,
                choices=choices
            )
        )

    def dump_options(self):
        """Returns json-compatible dict of options for roles.

        The current shape is influenced by current frontend, but it's flexible
        enough to withstand the test of time (new frontend would be able to
        adapt it to their needs easily).

        TODO: Be attentive to generalization for all vocabularies.
        """
        options = [
            {
                **({'icon': entry['icon']} if entry.get('icon') else {}),
                'text': _(entry.get(self.readable_key)),
                'value': key
            }
            for key, entry in self.data.items()
        ]

        return options
