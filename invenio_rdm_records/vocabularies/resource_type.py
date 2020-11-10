# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resource Type Vocabulary."""

from flask_babelex import lazy_gettext as _

from .vocabulary import Vocabulary


class ResourceTypeVocabulary(Vocabulary):
    """Encapsulates all resource type vocabulary data."""

    key_field = 'resource_type'

    @property
    def vocabulary_name(self):
        """Returns the human readable name for this vocabulary."""
        return 'resource type'

    def key(self, row):
        """Returns the primary key of the row.

        row: dict-like
        returns: serializable
        """
        return (row.get('type'), row.get('subtype', ''))

    def get_entry_by_dict(self, dict_key):
        """Returns a vocabulary entry as an OrderedDict."""
        if isinstance(dict_key, str):
            split = dict_key.split('-')
            if len(split) == 2:
                dict_key = {'type': split[0], 'subtype': dict_key}
            else:
                dict_key = {'type': dict_key}
        return super().get_entry_by_dict(dict_key)

    def get_title_by_dict(self, type_subtype):
        """Returns a vocabulary entry title."""
        entry = self.get_entry_by_dict(type_subtype)
        return entry.get('subtype_name') or entry.get('type_name')

    def get_invalid(self, type_subtype):
        """Returns the {<field>: <messages>} error dict for the given key."""
        types = sorted([k[0] for k in self.data.keys() if k[0]])
        _type = type_subtype.get('type')

        if not _type or (_type not in types):
            field = 'type'
            choices = types
        else:
            field = 'subtype'
            choices = sorted([
                k[1] for k in self.data.keys()
                if k[1] and k[0] == _type
            ])

        return {field: [_(f"Invalid value. Choose one of {choices}.")]}

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
