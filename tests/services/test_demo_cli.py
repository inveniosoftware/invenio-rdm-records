# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

import json

import pytest

from invenio_rdm_records.cli import create_fake_record
from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.records.models import RDMRecordMetadata


# TODO
@pytest.mark.skip()
def test_create_fake_record_saves_to_db(app, es_clear, location):
    """Test if fake records are saved to db."""
    # app needed for config overwrite of pidstore
    assert RDMRecordMetadata.query.first() is None

    created_record = create_fake_record()

    retrieved_record = RDMRecordMetadata.query.first()
    assert created_record._record.model == retrieved_record


def _assert_fields(fields, values, expected):
    for key in fields:
        assert values[key] == expected[key]


def _assert_single_hit(response, expected_record):
    assert response.status_code == 200

    search_hits = response.json['hits']['hits']

    # Kept for debugging
    for hit in search_hits:
        print("Search hit:", json.dumps(hit, indent=4, sort_keys=True))

    assert len(search_hits) == 1
    search_hit = search_hits[0]
    # only a record that has been published has an id, so we don't check for it
    root_fields = [
        'id', 'conceptid', 'created', 'updated', 'metadata', 'access',
    ]
    _assert_fields(root_fields, search_hit, expected_record)

    access_fields = [
        "record", "files", "owned_by", "embargo", "grants"
    ]
    _assert_fields(
        access_fields, search_hit['access'], expected_record['access'])

    metadata_fields = [
        'resource_type', 'creators', 'title', 'publication_date',
    ]
    _assert_fields(
        metadata_fields, search_hit['metadata'], expected_record['metadata'])


# TODO
@pytest.mark.skip()
def test_create_fake_record_saves_to_index(app, client, es_clear, location):
    """Test the creation of fake records and searching for them."""
    created_record = create_fake_record()
    # ES does not flush fast enough some times
    RDMRecord.index.refresh()

    response = client.get("/records")

    _assert_single_hit(response, created_record)
