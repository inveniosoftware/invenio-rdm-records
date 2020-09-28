# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

import json
from io import BytesIO

import pytest
from sqlalchemy.orm.exc import NoResultFound

HEADERS = {"content-type": "application/json", "accept": "application/json"}


@pytest.fixture
def draft_response(client, minimal_input_record, es_clear):
    """Bibliographic Draft fixture."""
    response = client.post(
        "/rdm-records", json=minimal_input_record, headers=HEADERS
    )
    return response


@pytest.mark.skip()
def test_create_draft_of_new_record(draft_response):
    """Test draft creation of a non-existing record."""
    assert draft_response.status_code == 201

    response_fields = set(draft_response.json.keys())
    expected_fields = set([
        'pid', 'metadata', 'revision', 'created', 'updated', 'links'
    ])
    assert expected_fields == response_fields


@pytest.mark.skip()
def test_record_draft_publish(client, draft_response):
    """Test draft publication of a non-existing record.

    It has to first create said draft and includes record read.
    """
    pid_value = draft_response.json['pid']

    # Publish it
    response = client.post(
        f"/rdm-records/{pid_value}/draft/actions/publish", headers=HEADERS
    )

    assert response.status_code == 202
    response_fields = set(response.json.keys())
    expected_fields = set([
        'pid', 'metadata', 'revision', 'created', 'updated', 'links'
    ])
    assert expected_fields == response_fields

    # Check draft deletion
    # TODO: Remove import when exception is properly handled
    with pytest.raises(NoResultFound):
        response = client.get(
            f"/rdm-records/{pid_value}/draft",
            headers=HEADERS
        )
    # assert response.status_code == 404

    # Test record exists
    response = client.get(f"/rdm-records/{pid_value}", headers=HEADERS)

    assert response.status_code == 200
    response_fields = set(response.json.keys())
    assert expected_fields == response_fields


@pytest.mark.skip()
def test_record_search(client, draft_response):
    pid_value = draft_response.json['pid']
    response = client.post(
        f"/rdm-records/{pid_value}/draft/actions/publish", headers=HEADERS
    )

    # Get published bibliographic records
    response = client.get('/rdm-records', headers=HEADERS)

    assert response.status_code == 200
    expected_response_keys = set(['hits', 'links', 'aggregations'])
    response_keys = set(response.json.keys())
    # The datamodel has other tests (jsonschemas, mappings, schemas)
    # Here we just want to crosscheck the important ones are there.
    assert expected_response_keys.issubset(response_keys)
    expected_metadata_keys = set([
        'access_right', 'resource_type', 'creators', 'titles'
    ])
    for r in response.json["hits"]["hits"]:
        metadata_keys = set(r["metadata"])
        assert expected_metadata_keys.issubset(metadata_keys)


@pytest.mark.skip(reason="Temporarily disabled since July sprint")
def test_simple_file_upload(app, client, draft_response):
    """Test simple file upload using REST API."""
    # Create record
    pid_value = draft_response.json['pid']
    response = client.post(
        f"/rdm-records/{pid_value}/draft/actions/publish", headers=HEADERS
    )
    assert response.status_code == 202

    response = client.put(
        f"/rdm-records/{pid_value}/files/example.txt",
        data=BytesIO(b"foo bar baz"),
        headers={"content-type": "application/octet-stream"}
    )

    assert response.status_code == 200
    assert response.json['key'] == 'example.txt'
    assert response.json['size'] != 0
