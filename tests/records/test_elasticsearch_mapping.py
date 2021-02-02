# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test Elasticsearch Mapping."""

import uuid

import pytest
from invenio_indexer.api import RecordIndexer
from invenio_jsonschemas import current_jsonschemas
from invenio_pidstore import current_pidstore
from invenio_records.api import Record
from marshmallow.fields import Bool, Integer, List
from marshmallow_utils.fields import ISODateString, SanitizedUnicode

from invenio_rdm_records.services.schemas.metadata_extensions import \
    add_es_metadata_extensions


@pytest.fixture(scope='module')
def app_config(app_config):
    """Override conftest.py's app_config
    """
    # Added custom configuration
    app_config['RDM_RECORDS_METADATA_NAMESPACES'] = {
        'dwc': {
            '@context': 'https://example.com/dwc/terms'
        },
        'nubiomed': {
            '@context': 'https://example.com/nubiomed/terms'
        }
    }

    app_config['RDM_RECORDS_METADATA_EXTENSIONS'] = {
        'dwc:family': {
            'elasticsearch': 'keyword',
            'marshmallow': SanitizedUnicode(required=True)
        },
        'dwc:behavior': {
            'elasticsearch': 'text',
            'marshmallow': SanitizedUnicode()
        },
        'nubiomed:number_in_sequence': {
            'elasticsearch': 'long',
            'marshmallow': Integer()
        },
        'nubiomed:scientific_sequence': {
            'elasticsearch': 'long',
            'marshmallow': List(Integer())
        },
        'nubiomed:original_presentation_date': {
            'elasticsearch': 'date',
            'marshmallow': DateString()
        },
        'nubiomed:right_or_wrong': {
            'elasticsearch': 'boolean',
            'marshmallow': Bool()
        }
    }

    return app_config


@pytest.fixture()
def minimal_record(appctx, minimal_record):
    data = {
        '$schema': (
            current_jsonschemas.path_to_url('records/record-v1.0.0.json')
        ),
        'publication_date': '2020-06-01'
    }
    minimal_record.update(data)
    return minimal_record


def assert_unordered_equality(array_dict1, array_dict2):
    array1 = sorted(array_dict1, key=lambda d: d['key'])
    array2 = sorted(array_dict2, key=lambda d: d['key'])
    assert array1 == array2


@pytest.mark.skip()
def test_metadata_extensions_mapping(db, es, minimal_record):
    """Tests that a Record is indexed into Elasticsearch properly.

    - Tests that the before_record_index_hook is registered properly.
    - Tests add_es_metadata_extensions.
    - Tests jsonschema validates correctly
    - Tests that retrieved record document is fine.

    NOTE:
        - es fixture depends on appctx fixture, so we are in app context
        - this test requires a running ES instance
    """
    data = {
        'extensions': {
            'dwc:family': 'Felidae',
            'dwc:behavior': 'Plays with yarn, sleeps in cardboard box.',
            'nubiomed:number_in_sequence': 3,
            'nubiomed:scientific_sequence': [1, 1, 2, 3, 5, 8],
            'nubiomed:original_presentation_date': '2019-02-14',
            'nubiomed:right_or_wrong': True,
        }
    }
    minimal_record.update(data)
    record_id = uuid.uuid4()
    current_pidstore.minters['recid_v2'](record_id, minimal_record)
    record = Record.create(minimal_record, id_=record_id)
    db.session.commit()
    indexer = RecordIndexer()

    index_result = indexer.index(record)

    _index = index_result['_index']
    _doc = index_result['_type']
    _id = index_result['_id']
    es_doc = es.get(index=_index, doc_type=_doc, id=_id)
    source = es_doc['_source']
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
    expected_booleans = [
        {
            'key': 'nubiomed:right_or_wrong',
            'value': True
        },
    ]
    assert_unordered_equality(source['extensions_keywords'], expected_keywords)
    assert_unordered_equality(source['extensions_texts'], expected_texts)
    assert_unordered_equality(source['extensions_longs'], expected_longs)
    assert_unordered_equality(source['extensions_dates'], expected_dates)
    assert_unordered_equality(
        source['extensions_booleans'], expected_booleans
    )


@pytest.mark.skip()
def test_publication_date_mapping(db, es, minimal_record):
    """Tests publication_date related fields are indexed properly.

    - Tests jsonschema validates correctly
    - Tests that retrieved record document is fine.

    NOTE:
        - es fixture depends on appctx fixture, so we are in app context
        - this test requires a running ES instance
    """
    # Interval
    minimal_record['publication_date'] = '1939/1945'
    minimal_record['_publication_date_search'] = '1939-01-01'

    record_id = uuid.uuid4()
    current_pidstore.minters['recid_v2'](record_id, minimal_record)
    record = Record.create(minimal_record, id_=record_id)
    db.session.commit()
    indexer = RecordIndexer()

    index_result = indexer.index(record)

    _index = index_result['_index']
    _doc = index_result['_type']
    _id = index_result['_id']
    es_doc = es.get(index=_index, doc_type=_doc, id=_id)
    source = es_doc['_source']
    assert source['publication_date'] == '1939/1945'
    assert source['_publication_date_search'] == '1939-01-01'
