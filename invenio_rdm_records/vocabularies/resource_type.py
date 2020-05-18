# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resource Type Vocabulary."""

import csv
from collections import OrderedDict

from flask_babelex import lazy_gettext as _

from .utils import hierarchized_rows


class ResourceTypeVocabulary(object):
    """Encapsulates all resource type vocabulary data."""

    def __init__(self, path):
        """Constructor."""
        self.path = path
        self._load_data()

    def _load_data(self):
        """Sets self.data with the filled rows."""
        with open(self.path) as f:
            reader = csv.DictReader(f, skipinitialspace=True)
            # NOTE: We use an OrderedDict to preserve on file row order
            self.data = OrderedDict([
                # NOTE: unfilled cells return '' (empty string)
                ((row['type'], row['subtype']), row)
                for row in hierarchized_rows(reader)
            ])

    def get_entry_by_dict(self, type_subtype):
        """Returns a vocabulary entry as an OrderedDict."""
        return self.data.get(
            (type_subtype['type'], type_subtype.get('subtype', ''))
        )

    def get_title_by_dict(self, type_subtype):
        """Returns a vocabulary entry title."""
        entry = self.get_entry_by_dict(type_subtype)

        # NOTE: translations could also be done via the CSV file directly
        result = _(entry.get('type_name'))
        if entry.get('subtype_name'):
            subtype_name = _(entry.get('subtype_name'))
            result += " / " + subtype_name

        return result

    def get_invalid(self, type_subtype):
        """Returns the error message for the given dict key."""
        # TODO: Revisit with deposit to return targeted error message
        types = set([k[0] for k in self.data.keys()])
        _type = type_subtype.get('type')
        if not _type or (_type not in types):
            _input = _type
            choices = types
        else:
            _input = type_subtype.get('subtype')
            choices = set([k[1] for k in self.data.keys()])

        return _(
            'Invalid resource type. {input} not one of {choices}'.format(
                input=_input,
                choices=choices
            )
        )

    def dump_options(self):
        """Returns json-compatible dict of options for type and subtype.

        The current shape is influenced by current frontend, but it's flexible
        enough to withstand the test of time (new frontend would be able to
        adapt it to their needs easily).

        TODO: Be attentive to generalization for all vocabularies.
        """
        options = {'type': [], 'subtype': []}

        for (_type, subtype), entry in self.data.items():
            type_option = {
                'icon': entry.get('type_icon'),
                'text': _(entry.get('type_name')),
                'value': _type
            }

            if type_option not in options['type']:
                options['type'].append(type_option)

            # NOTE: There isn't always a subtype
            if subtype:
                subtype_option = {
                    'parent-text': type_option['text'],
                    'parent-value': type_option['value'],
                    'text': _(entry.get('subtype_name')),
                    'value': subtype,
                }

                # These are not duplicated so we can just append
                options['subtype'].append(subtype_option)

        return options
