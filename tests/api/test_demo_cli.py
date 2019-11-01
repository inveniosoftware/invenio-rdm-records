# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University,
#                    Galter Health Sciences Library & Learning Center.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function

import json

from invenio_records.models import RecordMetadata
from invenio_search import current_search

from invenio_rdm_records.cli import create_fake_record


def test_create_fake_record_saves_to_db(es_clear, location):
    """Test simple flow using REST API."""
    assert RecordMetadata.query.first() is None

    created_record = create_fake_record()

    retrieved_record = RecordMetadata.query.first()
    assert created_record.model == retrieved_record


def assert_single_hit(response, expected_record):
    assert response.status_code == 200

    search_hits = response.json['hits']['hits']

    # Kept for debugging
    for hit in search_hits:
        print("Search hit:", json.dumps(hit, indent=4, sort_keys=True))

    assert len(search_hits) == 1
    search_hit = search_hits[0]
    # only a record that has been published has an id, so we don't check for it
    for key in ['created', 'updated', 'metadata', 'links']:
        assert key in search_hit

    required_fields = [
        'access_right',
        'contributors',
        'description',
        'owners',
        'publication_date',
        'recid',
        'resource_type',
        'title',
    ]
    for key in required_fields:
        expected_value = expected_record[key]
        if key == 'publication_date':
            expected_value = expected_value[:10]
        assert search_hit['metadata'][key] == expected_value


def test_create_fake_record_saves_to_index(client, es_clear, location):
    created_record = create_fake_record()

    response = client.get("/records/")

    assert_single_hit(response, created_record)
