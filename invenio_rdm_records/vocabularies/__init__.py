# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Models for Invenio RDM Records."""

from os.path import dirname, join

from flask import current_app
from flask_babelex import lazy_gettext as _

from .contributor_role import ContributorRoleVocabulary
from .resource_type import ResourceTypeVocabulary
from .utils import hierarchized_rows


class Vocabulary(object):
    """Interface to vocabulary data."""

    this_dir = dirname(__file__)
    vocabularies = {
        # NOTE: dotted keys should parallel MetadataSchemaV1 fields
        'resource_type': {
            'path': join(this_dir, 'resource_types.csv'),
            'class': ResourceTypeVocabulary,
            'object': None
        },
        'contributors.role': {
            'path': join(this_dir, 'contributor_role.csv'),
            'class': ContributorRoleVocabulary,
            'object': None
        }
    }

    @classmethod
    def get_vocabulary(cls, key):
        """Returns the Vocabulary object corresponding to the path.

        :param key: string of dotted subkeys for Vocabulary object.
        """

        vocabulary_dict = cls.vocabularies.get(key)

        if not vocabulary_dict:
            return None

        obj = vocabulary_dict.get('object')

        if not obj:
            custom_vocabulary_dict = (
                current_app.config
                .get('RDM_RECORDS_CUSTOM_VOCABULARIES', {})
                .get(key, {})
            )

            path = (
                custom_vocabulary_dict.get('path') or
                vocabulary_dict.get('path')
            )

            # Only predefined classes for now
            VocabularyClass = vocabulary_dict['class']
            obj = VocabularyClass(path)
            vocabulary_dict['object'] = obj

        return obj

    @classmethod
    def clear(cls):
        """Clears loaded vocabularies."""
        def _clear(vocabulary_dict):
            """Clear out Vocabulary object."""
            if (isinstance(vocabulary_dict, dict) and
                    'object' in vocabulary_dict):
                vocabulary_dict['object'] = None
            elif isinstance(vocabulary_dict, dict):
                for value in vocabulary_dict.values():
                    _clear(value)
            else:
                pass

        _clear(cls.vocabularies)


def dump_vocabularies(vocabulary_singleton):
    """Returns a json-compatible dict of options for frontend.

    The current shape is influenced by current frontend, but it's flexible
    enough to withstand the test of time (new frontend would be able to
    change it easily).
    """
    options = {}
    # sign to move this to the class
    for key in vocabulary_singleton.vocabularies:
        result = options
        for i, dotkey in enumerate(key.split('.')):
            if i == (len(key.split('.')) - 1):
                result[dotkey] = vocabulary_singleton.get_vocabulary(key).dump_options()  # noqa
            else:
                result.setdefault(dotkey, {})
                result = result[dotkey]

    return options
