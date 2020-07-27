# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

import json

import pytest
from sqlalchemy.orm.exc import NoResultFound

HEADERS = {"content-type": "application/json", "accept": "application/json"}


def test_create_draft_of_new_record(client, minimal_record):
    """Test draft creation of a non-existing record."""
    response = client.post(
        "/rdm-records", data=json.dumps(minimal_record), headers=HEADERS
    )

    assert response.status_code == 201
    response_fields = response.json.keys()
    fields_to_check = ['pid', 'metadata', 'revision',
                       'created', 'updated', 'links']

    for field in fields_to_check:
        assert field in response_fields


def test_record_draft_publish(client, minimal_record):
    """Test draft publication of a non-existing record.

    It has to first create said draft and includes record read.
    """
    # Create the draft
    response = client.post(
        "/rdm-records", data=json.dumps(minimal_record), headers=HEADERS
    )

    assert response.status_code == 201
    recid = response.json['pid']

    # Publish it
    response = client.post(
        "/rdm-records/{}/draft/actions/publish".format(recid), headers=HEADERS
    )

    assert response.status_code == 200
    response_fields = response.json.keys()
    fields_to_check = ['pid', 'metadata', 'revision',
                       'created', 'updated', 'links']

    for field in fields_to_check:
        assert field in response_fields

    # Check draft deletion
    # TODO: Remove import when exception is properly handled
    with pytest.raises(NoResultFound):
        response = client.get(
            "/rdm-records/{}/draft".format(recid),
            headers=HEADERS
        )
    # assert response.status_code == 404

    # Test record exists
    response = client.get("/rdm-records/{}".format(recid), headers=HEADERS)

    assert response.status_code == 200

    response_fields = response.json.keys()
    fields_to_check = ['pid', 'metadata', 'revision',
                       'created', 'updated', 'links']

    for field in fields_to_check:
        assert field in response_fields


def test_record_search(client):
    """Test draft creation."""
    expected_response_keys = set(['hits', 'links', 'aggregations'])
    expected_metadata_keys = set([
        'access_right', 'resource_type', 'creators', 'titles'
    ])

    # Get published bibliographic records
    response = client.get('/rdm-records', headers=HEADERS)

    assert response.status_code == 200
    response_keys = set(response.json.keys())
    # The datamodel has other tests (jsonschemas, mappings, schemas)
    # Here we just want to crosscheck the important ones are there.
    assert expected_response_keys.issubset(response_keys)

    for r in response.json["hits"]["hits"]:
        metadata_keys = set(r["metadata"])
        assert expected_metadata_keys.issubset(metadata_keys)
