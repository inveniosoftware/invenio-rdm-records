# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test Serialization to Elasticsearch dump."""

import pytest
from invenio_records_rest.schemas.fields import DateString, SanitizedUnicode
from marshmallow.fields import Float, Integer, List

from invenio_rdm_records.metadata_extensions import add_es_metadata_extensions


@pytest.fixture(scope='module')
def app_config(app_config):
    """Override conftest.py's app_config
    """
    # supported_configurations = [
    #     'FILES_REST_PERMISSION_FACTORY',
    #     'PIDSTORE_RECID_FIELD',
    #     'RECORDS_REST_ENDPOINTS',
    #     'RECORDS_REST_FACETS',
    #     'RECORDS_REST_SORT_OPTIONS',
    #     'RECORDS_REST_DEFAULT_SORT',
    #     'RECORDS_FILES_REST_ENDPOINTS',
    #     'RECORDS_PERMISSIONS_RECORD_POLICY'
    # ]

    # for config_key in supported_configurations:
    #     app_config[config_key] = getattr(config, config_key, None)

    # Added custom configuration
    app_config['RDM_RECORDS_METADATA_EXTENSIONS'] = {
        'dwc': {
            'family': {
                'types': {
                    'elasticsearch': 'keyword',
                    'marshmallow': SanitizedUnicode(required=True)
                }
            },
            'behavior': {
                'types': {
                    'marshmallow': SanitizedUnicode(),
                    'elasticsearch': 'text',
                }
            }
        },
        'nubiomed': {
            'number_in_sequence': {
                'types': {
                    'elasticsearch': 'long',
                    'marshmallow': Integer()
                }
            },
            'scientific_sequence': {
                'types': {
                    'elasticsearch': 'long',
                    'marshmallow': List(Integer())
                }
            },
            'original_presentation_date': {
                'types': {
                    'elasticsearch': 'date',
                    'marshmallow': DateString()
                }
            }
        }
    }

    return app_config


def test_add_es_metadata_extensions(appctx):
    record = {
        # contains other fields, but we only care about 'extensions' field
        'extensions': {
            'dwc:family': 'Felidae',
            'dwc:behavior': 'Plays with yarn, sleeps in cardboard box.',
            'nubiomed:number_in_sequence': 3,
            'nubiomed:scientific_sequence': [1, 1, 2, 3, 5, 8],
            # TODO: should this be a string or a Date?
            'nubiomed:original_presentation_date': '2019-02-14',
        }
    }

    add_es_metadata_extensions(record)
    # TODO: make sure to ignore 'extensions' in mapping schema --
    # test with live index

    expected_keywords = [
        {'key': 'dwc:family', 'value': 'Felidae'},
    ]
    expected_texts = [
        {
            'key': 'dwc:behavior',
            'value': 'Plays with yarn, sleeps in cardboard box.'
        },
    ]
    expected_longs = [
        {
            'key': 'nubiomed:number_in_sequence',
            'value': 3
        },
        {'key': 'nubiomed:scientific_sequence', 'value': [1, 1, 2, 3, 5, 8]},
    ]
    expected_dates = [
        {
            'key': 'nubiomed:original_presentation_date',
            'value': '2019-02-14'
        },
    ]

    def assert_unordered_equality(array_dict1, array_dict2):
        array1 = sorted(array_dict1, key=lambda d: d['key'])
        # [
        #     (d['key'], d['value']) for d in array_dict1
        # ]
        array2 = sorted(array_dict2, key=lambda d: d['key'])
        # [
        #     (d['key'], d['value']) for d in array_dict2
        # ]

        print('array1', array1)
        print('array2', array2)
        assert array1 == array2

    assert_unordered_equality(record['extensions_keywords'], expected_keywords)
    assert_unordered_equality(record['extensions_texts'], expected_texts)
    assert_unordered_equality(record['extensions_longs'], expected_longs)
    assert_unordered_equality(record['extensions_dates'], expected_dates)
