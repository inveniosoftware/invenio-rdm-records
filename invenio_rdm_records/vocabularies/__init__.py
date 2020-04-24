# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Models for Invenio RDM Records."""

import csv
import json
from collections import OrderedDict, defaultdict
from os.path import dirname, join

from flask import current_app
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
        """Returns json-compatible key-part: texts and the values.

        The current shape is influenced by current frontend, but it's flexible
        enough to withstand the test of time (new frontend would be able to
        change it easily).

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

            subtype_option = {
                'parent-text': type_option['text'],
                'parent-value': type_option['value'],
                'text': _(entry.get('subtype_name')),
                'value': subtype,
            }

            # These are not duplicated so we can just append
            options['subtype'].append(subtype_option)

        return options


class Vocabulary(object):
    """Interface to vocabulary data."""

    this_dir = dirname(__file__)
    vocabularies = {
        # NOTE: keys should be same as MetadataSchemaV1 fields
        'resource_type': {
            'path': join(this_dir, 'resource_types.csv'),
            'class': ResourceTypeVocabulary,
            'object': None
        }
    }

    @classmethod
    def get_vocabulary(cls, vocabulary_type):
        """Returns the corresponding Vocabulary object."""
        obj = cls.vocabularies.get(vocabulary_type, {}).get('object')
        if not obj:
            path = (
                current_app.config
                .get('RDM_RECORDS_CUSTOM_VOCABULARIES', {})
                .get(vocabulary_type) or
                cls.vocabularies
                .get(vocabulary_type)
                .get('path')
            )
            # Only predefined classes for now
            VocabularyClass = cls.vocabularies[vocabulary_type]['class']
            obj = VocabularyClass(path)
            cls.vocabularies[vocabulary_type]['object'] = obj

        return obj

    @classmethod
    def clear(cls):
        """Clears loaded vocabularies."""
        for vocabulary in cls.vocabularies.values():
            vocabulary['object'] = None


def dump_vocabularies(vocabulary_singleton):
    """Returns a json-compatible dict of options for frontend.

    The current shape is influenced by current frontend, but it's flexible
    enough to withstand the test of time (new frontend would be able to
    change it easily).
    """
    vocabularies = vocabulary_singleton.vocabularies
    return {
        field: vocabulary_singleton.get_vocabulary(field).dump_options()
        for field in vocabularies
    }
