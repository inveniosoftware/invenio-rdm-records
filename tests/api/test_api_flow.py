# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

import json
from io import BytesIO

from invenio_search import current_search


def _assert_single_hit(response, expected_record):
    assert response.status_code == 200

    search_hits = response.json['hits']['hits']

    # Kept for debugging
    for hit in search_hits:
        print("Search hit:", json.dumps(hit, indent=4, sort_keys=True))

    assert len(search_hits) == 1

    search_hit = search_hits[0]
    for key in ['created', 'updated', 'metadata', 'links']:
        assert key in search_hit

    assert search_hit['metadata']['titles'] == expected_record['titles']


def test_simple_flow(client, location, full_input_record):
    """Test simple flow using REST API."""
    url = 'https://localhost:5000/records/'

    # create a record
    response = client.post(url, json=full_input_record)
    assert response.status_code == 201
    current_search.flush_and_refresh('records')

    # retrieve records
    response = client.get(url)
    _assert_single_hit(response, full_input_record)


def test_simple_file_upload(client, location, full_input_record):
    """Test simple file upload using REST API."""
    # Create record
    records_url = 'https://localhost:5000/records/'
    response = client.post(records_url, json=full_input_record)
    assert response.status_code == 201
    current_search.flush_and_refresh('records')

    # Attach file to record
    recid = response.json['id']
    files_url = records_url + "{}/files/example.txt".format(recid)
    headers = [("Content-Type", "application/octet-stream")]
    response = client.put(
        files_url, data=BytesIO(b"foo bar baz"), headers=headers)

    assert response.status_code == 200
    assert response.json['key'] == 'example.txt'
    assert response.json['size'] != 0

    # Retrieve record
    record_url = records_url + "{}".format(recid)
    response = client.get(record_url)

    expected_files_url = (
        'https://localhost:5000/records/{}/files'.format(recid)
    )
    assert response.json['links']['files'] == expected_files_url
