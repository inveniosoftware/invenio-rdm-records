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

from invenio_rdm_records.records import BibliographicRecord


@pytest.fixture()
def headers():
    """Default headers for making requests."""
    return {
        'content-type': 'application/json',
        'accept': 'application/json',
    }


@pytest.fixture()
def ui_headers():
    """Default headers for making requests."""
    return {
        'content-type': 'application/json',
        'accept': 'application/vnd.inveniordm.v1+json',
    }


def _assert_single_item_response(response):
    """Assert the fields present on a single item response."""
    response_fields = response.json.keys()
    fields_to_check = ['id', 'conceptid', 'metadata',
                       'created', 'updated', 'links']

    for field in fields_to_check:
        assert field in response_fields


def test_simple_flow(app, client, minimal_record, headers):
    """Test a simple REST API flow."""
    # Create a draft
    created_draft = client.post(
        '/records', headers=headers, data=json.dumps(minimal_record))
    assert created_draft.status_code == 201
    _assert_single_item_response(created_draft)
    id_ = created_draft.json["id"]

    # Read the draft
    read_draft = client.get(f'/records/{id_}/draft', headers=headers)
    assert read_draft.status_code == 200
    assert read_draft.json['metadata'] == created_draft.json['metadata']

    # Update and save draft
    data = read_draft.json
    data["metadata"]["title"] = 'New title'

    res = client.put(
        f'/records/{id_}/draft', headers=headers, data=json.dumps(data))
    assert res.status_code == 200
    assert res.json['metadata']["title"] == 'New title'

    # Publish it
    response = client.post(
        "/records/{}/draft/actions/publish".format(id_), headers=headers)

    # Check record was created
    recid = response.json["id"]
    response = client.get("/records/{}".format(recid), headers=headers)
    assert response.status_code == 200

    created_record = response.json

    BibliographicRecord.index.refresh()

    # Search it
    res = client.get(
        f'/records', query_string={'q': f'id:{recid}'}, headers=headers)
    assert res.status_code == 200
    assert res.json['hits']['total'] == 1
    assert res.json['hits']['hits'][0]['metadata'] == \
        created_record['metadata']
    data = res.json['hits']['hits'][0]
    assert data['metadata']['title'] == 'New title'


def test_create_draft(client, minimal_record, headers):
    """Test draft creation of a non-existing record."""
    response = client.post(
        "/records", data=json.dumps(minimal_record), headers=headers)

    assert response.status_code == 201
    _assert_single_item_response(response)


def test_read_draft(client, minimal_record, headers):
    """Test draft read."""
    response = client.post(
        "/records", data=json.dumps(minimal_record), headers=headers)

    assert response.status_code == 201

    recid = response.json['id']
    response = client.get(
        "/records/{}/draft".format(recid), headers=headers)

    assert response.status_code == 200

    _assert_single_item_response(response)


def test_update_draft(client, minimal_record, headers):
    """Test draft update."""
    response = client.post(
        "/records", data=json.dumps(minimal_record), headers=headers)

    assert response.status_code == 201
    assert response.json['metadata']["title"] == \
        minimal_record['metadata']["title"]

    recid = response.json['id']

    orig_title = minimal_record['metadata']["title"]
    edited_title = "Edited title"
    minimal_record['metadata']["title"] = edited_title

    # Update draft content
    update_response = client.put(
        "/records/{}/draft".format(recid),
        data=json.dumps(minimal_record),
        headers=headers
    )

    assert update_response.status_code == 200
    assert update_response.json["metadata"]["title"] == \
        edited_title
    assert update_response.json["id"] == recid

    # Check the updates where saved
    update_response = client.get(
        "/records/{}/draft".format(recid), headers=headers)

    assert update_response.status_code == 200
    assert update_response.json["metadata"]["title"] == \
        edited_title
    assert update_response.json["id"] == recid


def test_delete_draft(client, minimal_record, headers):
    """Test draft deletion."""
    response = client.post(
        "/records", data=json.dumps(minimal_record), headers=headers)

    assert response.status_code == 201

    recid = response.json['id']

    update_response = client.delete(
        "/records/{}/draft".format(recid), headers=headers)

    assert update_response.status_code == 204

    # Check draft deletion
    # FIXME: Remove import when exception is properly handled
    with pytest.raises(NoResultFound):
        update_response = client.get(
            "/records/{}/draft".format(recid), headers=headers)

        assert update_response.status_code == 404


def _create_and_publish(client, minimal_record, headers):
    """Create a draft and publish it."""
    # Create the draft
    response = client.post(
        "/records", data=json.dumps(minimal_record), headers=headers)

    assert response.status_code == 201
    recid = response.json['id']

    # Publish it
    response = client.post(
        "/records/{}/draft/actions/publish".format(recid), headers=headers)

    assert response.status_code == 202
    _assert_single_item_response(response)

    return recid


def test_publish_draft(client, minimal_record, headers):
    """Test draft publication of a non-existing record.

    It has to first create said draft.
    """
    recid = _create_and_publish(client, minimal_record, headers)

    # Check draft does not exists anymore
    # FIXME: Remove import when exception is properly handled
    with pytest.raises(NoResultFound):
        response = client.get(
            "/records/{}/draft".format(recid), headers=headers)

        assert response.status_code == 404

    # Check record exists
    response = client.get("/records/{}".format(recid), headers=headers)

    assert response.status_code == 200

    _assert_single_item_response(response)


def test_create_publish_new_revision(client, minimal_record,
                                     identity_simple, headers):
    """Test draft creation of an existing record and publish it."""
    recid = _create_and_publish(client, minimal_record, headers)

    # # FIXME: Allow ES to clean deleted documents.
    # # Flush is not the same. Default collection time is 1 minute.
    # time.sleep(70)

    # Create new draft of said record
    orig_title = minimal_record["metadata"]["title"]
    minimal_record["metadata"]["title"] = "Edited title"
    response = client.post(
        "/records/{}/draft".format(recid),
        headers=headers
    )

    assert response.status_code == 201
    assert response.json['revision_id'] == 4
    _assert_single_item_response(response)

    # Update that new draft
    response = client.put(
        "/records/{}/draft".format(recid),
        data=json.dumps(minimal_record),
        headers=headers
    )

    assert response.status_code == 200

    # Check the actual record was not modified
    response = client.get(
        "/records/{}".format(recid), headers=headers)

    assert response.status_code == 200
    _assert_single_item_response(response)
    assert response.json['metadata']["title"] == orig_title

    # Publish it to check the increment in reversion
    response = client.post(
        "/records/{}/draft/actions/publish".format(recid), headers=headers)

    assert response.status_code == 202
    _assert_single_item_response(response)

    assert response.json['id'] == recid
    assert response.json['revision_id'] == 2
    assert response.json['metadata']["title"] == \
        minimal_record["metadata"]["title"]

    # Check it was actually edited
    response = client.get(
        "/records/{}".format(recid), headers=headers)

    assert response.json["metadata"]["title"] == \
        minimal_record["metadata"]["title"]


def test_ui_data_in_record(
        app, client, minimal_record, headers, ui_headers):
    """Publish a record and check that it contains the UI data."""
    recid = _create_and_publish(client, minimal_record, headers)

    BibliographicRecord.index.refresh()

    # Check if list results contain UI data
    response = client.get(
        '/records', query_string={'q': f'id:{recid}'}, headers=ui_headers)
    assert response.json['hits']['hits'][0]['ui']

    # Check if item results contain UI data
    response = client.get(f'/records/{recid}', headers=ui_headers)
    assert response.json['ui']
