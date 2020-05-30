# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

import os

from flask_babelex import lazy_gettext as _

from invenio_rdm_records.marshmallow.json import MetadataSchemaV1, dump_empty
from invenio_rdm_records.vocabularies import Vocabularies


def test_dumping_empty_record():
    empty_record = dump_empty(MetadataSchemaV1())

    assert empty_record == {
        '_access': {'files_restricted': None, 'metadata_restricted': None},
        '_default_preview': None,
        '_communities': None,
        '_contact': None,
        '_created_by': None,
        '_embargo_date': None,
        '_files': [
            {
                'bucket': None,
                'checksum': None,
                'key': None,
                'links': None,
                'size': None,
                'type': None
            }
        ],
        '_internal_notes': [
            {
                'user': None,
                'timestamp': None,
                'note': None
            }
        ],
        '_owners': [None],
        'access_right': None,
        'contributors': [
            {
                'affiliations': [
                    {
                        'name': None,
                        'identifier': None,
                        'scheme': None
                    }
                ],
                'family_name': None,
                'given_name': None,
                'identifiers': None,
                'name': None,
                'role': None,
                'type': None,
            }
        ],
        'creators': [
            {
                'affiliations': [
                    {
                        'name': None,
                        'identifier': None,
                        'scheme': None
                    }
                ],
                'family_name': None,
                'given_name': None,
                'identifiers': None,
                'name': None,
                'type': None,
            }
        ],
        'dates': [
            {
                'type': None,
                'end': None,
                'description': None,
                'start': None
            }
        ],
        'extensions': None,
        'descriptions': [
            {
                'type': None,
                'lang': None,
                'description': None
            }
        ],
        'language': None,
        'locations': [
            {
                'description': None,
                'point': {
                    'lon': None,
                    'lat': None
                },
                'place': None
            }
        ],
        'licenses': [
            {
                'identifier': None,
                'scheme': None,
                'uri': None,
                'license': None
            }
        ],
        'version': None,
        'publication_date': None,
        'references': [
            {
                'scheme': None,
                'reference_string': None,
                'identifier': None
            }
        ],
        'related_identifiers': [
            {
                'resource_type': {
                    'subtype': None,
                    'type': None
                },
                'scheme': None,
                'relation_type': None,
                'identifier': None
            }
        ],
        'resource_type': {
            'subtype': None,
            'type': None
        },
        'subjects': [{'subject': None, 'identifier': None, 'scheme': None}],
        'titles': [
            {
                'type': None,
                'lang': None,
                'title': None
            }
        ],
        # TODO: Investigate the impact of these 2 fields on
        #       frontend to backend to frontend flow
        'identifiers': None,
        'recid': None
    }


def test_dump_resource_type(config, vocabulary_clear):
    prev_config = config.get('RDM_RECORDS_CUSTOM_VOCABULARIES')
    config['RDM_RECORDS_CUSTOM_VOCABULARIES'] = {
        'resource_type': {
            'path': os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'data',
                'resource_types.csv'
            )
        },
    }

    dumped_vocabularies = Vocabularies.dump()

    assert dumped_vocabularies['resource_type'] == {
        'type': [
            {
                'icon': 'file alternate',
                'text': _('Publication'),
                'value': 'publication',
            },
            {
                'icon': 'chart bar outline',
                'text': _('Image'),
                'value': 'my_image',
            },
            {
                'icon': 'code',
                'text': _('Software'),
                'value': 'software',
            }
        ],
        'subtype': [
            {
                'parent-text': _('Publication'),
                'parent-value': 'publication',
                'text': _('Book'),
                'value': 'publication-book',
            },
            {
                'parent-text': _('Image'),
                'parent-value': 'my_image',
                'text': _('Photo'),
                'value': 'my_photo',
            }
        ]
    }

    config['RDM_RECORDS_CUSTOM_VOCABULARIES'] = prev_config


def test_dump_contributors_role(config, vocabulary_clear):
    prev_config = config.get('RDM_RECORDS_CUSTOM_VOCABULARIES')
    config['RDM_RECORDS_CUSTOM_VOCABULARIES'] = {
        'contributors.role': {
            'path': os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'data',
                'contributor_role.csv'
            )
        },
    }

    dumped_vocabularies = Vocabularies.dump()

    assert dumped_vocabularies['contributors']['role'] == [
        {
            'value': 'Librarian',
            'text': _('Librarian')
        },
        {
            'value': 'DataCollector',
            'text': _('Data Collector')
        }
    ]

    config['RDM_RECORDS_CUSTOM_VOCABULARIES'] = prev_config


def test_dump_titles_type(config, vocabulary_clear):
    prev_config = config.get('RDM_RECORDS_CUSTOM_VOCABULARIES')
    config['RDM_RECORDS_CUSTOM_VOCABULARIES'] = {
        'titles.type': {
            'path': os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'data',
                'title_type.csv'
            )
        }
    }

    dumped_vocabularies = Vocabularies.dump()

    assert dumped_vocabularies['titles']['type'] == [
        {
            'value': 'AlternateTitle',
            'text': _('Alternate Title')
        }
    ]

    config['RDM_RECORDS_CUSTOM_VOCABULARIES'] = prev_config


def test_dump_access_right(config, vocabulary_clear):
    prev_config = config.get('RDM_RECORDS_CUSTOM_VOCABULARIES')
    config['RDM_RECORDS_CUSTOM_VOCABULARIES'] = {
        'access_right': {
            'path': os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'data',
                'access_right.csv'
            )
        }
    }

    dumped_vocabularies = Vocabularies.dump()

    assert dumped_vocabularies['access_right'] == [
        {
            'icon': 'lock open',
            'value': 'open',
            'text': _('Open Access')
        },
    ]

    config['RDM_RECORDS_CUSTOM_VOCABULARIES'] = prev_config
