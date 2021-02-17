# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

import json

import arrow
import pytest

from invenio_rdm_records.records import RDMDraft, RDMRecord


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
    fields_to_check = [
        'access', 'conceptid', 'created', 'id', 'links', 'metadata', 'updated'
    ]

    for field in fields_to_check:
        assert field in response_fields


def _validate_access(response, original):
    """Validate that the record's access is as specified."""
    assert "access" in response

    access, orig_access = response["access"], original["access"]
    assert len(access["owned_by"]) > 0
    assert access["record"] == orig_access["record"]
    assert access["files"] == orig_access["files"]

    if orig_access.get("embargo"):
        assert "embargo" in access
        embargo, orig_embargo = access["embargo"], orig_access["embargo"]

        until = arrow.get(embargo["until"]).datetime
        orig_until = arrow.get(orig_embargo["until"]).datetime
        assert until.strftime("%Y-%m-%d") == orig_until.strftime("%Y-%m-%d")

        if embargo.get("reason"):
            assert embargo.get("reason") == orig_embargo.get("reason")

        assert embargo.get("active") == orig_embargo.get("active")


def test_simple_flow(
    app, client_with_login, location, minimal_record, headers, es_clear
):
    client = client_with_login
    """Test a simple REST API flow."""
    # Create a draft
    created_draft = client.post(
        '/records', headers=headers, data=json.dumps(minimal_record))
    assert created_draft.status_code == 201
    _assert_single_item_response(created_draft)
    _validate_access(created_draft.json, minimal_record)
    id_ = created_draft.json["id"]

    # Read the draft
    read_draft = client.get(f'/records/{id_}/draft', headers=headers)
    assert read_draft.status_code == 200
    assert read_draft.json['metadata'] == created_draft.json['metadata']
    _validate_access(read_draft.json, minimal_record)

    # Update and save draft
    data = read_draft.json
    data["metadata"]["title"] = 'New title'

    res = client.put(
        f'/records/{id_}/draft', headers=headers, data=json.dumps(data))
    assert res.status_code == 200
    assert res.json['metadata']["title"] == 'New title'
    _validate_access(res.json, minimal_record)

    # Publish it
    response = client.post(
        "/records/{}/draft/actions/publish".format(id_), headers=headers)

    # Check record was created
    recid = response.json["id"]
    response = client.get("/records/{}".format(recid), headers=headers)
    assert response.status_code == 200
    _validate_access(response.json, minimal_record)

    created_record = response.json

    RDMRecord.index.refresh()

    # Search it
    res = client.get(
        f'/records', query_string={'q': f'id:{recid}'}, headers=headers)
    assert res.status_code == 200
    assert res.json['hits']['total'] == 1
    assert res.json['hits']['hits'][0]['metadata'] == \
        created_record['metadata']
    data = res.json['hits']['hits'][0]
    assert data['metadata']['title'] == 'New title'
    _validate_access(data, minimal_record)


def test_create_draft(
    client_with_login, location, minimal_record, headers, es_clear
):
    """Test draft creation of a non-existing record."""
    client = client_with_login
    response = client.post(
        "/records", data=json.dumps(minimal_record), headers=headers)

    assert response.status_code == 201
    _assert_single_item_response(response)
    _validate_access(response.json, minimal_record)


def test_create_partial_draft(
    client_with_login, location, minimal_record, headers, es_clear
):
    """Test partial draft creation of a non-existing record.

    NOTE: This tests functionality implemented in records/drafts-resources, but
          intentions specific to this module.
    """
    client = client_with_login
    minimal_record['metadata']["title"] = ""
    response = client.post("/records", json=minimal_record, headers=headers)

    assert 201 == response.status_code
    _assert_single_item_response(response)
    errors = [
        {
            "field": "metadata.title",
            "messages": ["Shorter than minimum length 3."]
        },
    ]
    assert errors == response.json["errors"]


def test_read_draft(
    client_with_login, location, minimal_record, headers, es_clear
):
    """Test draft read."""
    client = client_with_login
    response = client.post(
        "/records", data=json.dumps(minimal_record), headers=headers)

    assert response.status_code == 201

    recid = response.json['id']
    response = client.get(
        "/records/{}/draft".format(recid), headers=headers)

    assert response.status_code == 200

    _assert_single_item_response(response)
    _validate_access(response.json, minimal_record)


def test_update_draft(
    client_with_login, location, minimal_record, headers, es_clear
):
    """Test draft update."""
    client = client_with_login
    response = client.post(
        "/records", data=json.dumps(minimal_record), headers=headers)

    assert response.status_code == 201
    assert response.json['metadata']["title"] == \
        minimal_record['metadata']["title"]
    _validate_access(response.json, minimal_record)

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
    _validate_access(update_response.json, minimal_record)

    # Check the updates where saved
    update_response = client.get(
        "/records/{}/draft".format(recid), headers=headers)

    assert update_response.status_code == 200
    assert update_response.json["metadata"]["title"] == \
        edited_title
    assert update_response.json["id"] == recid
    _validate_access(update_response.json, minimal_record)


def test_update_partial_draft(
    client_with_login, location, minimal_record, headers, es_clear
):
    """Test partial draft update.

    NOTE: This tests functionality implemented in records/drafts-resources, but
          intentions specific to this module.
    """
    client = client_with_login
    response = client.post("/records", json=minimal_record, headers=headers)
    assert 201 == response.status_code
    recid = response.json['id']
    minimal_record['metadata']["title"] = ""

    # Update draft content
    response = client.put(
        f"/records/{recid}/draft",
        json=minimal_record,
        headers=headers
    )

    assert 200 == response.status_code
    _assert_single_item_response(response)
    errors = [
        {
            "field": "metadata.title",
            "messages": ["Shorter than minimum length 3."]
        },
    ]
    assert errors == response.json["errors"]

    # The draft has had its title erased
    response = client.get(f"/records/{recid}/draft", headers=headers)
    assert 200 == response.status_code
    assert "title" not in response.json["metadata"]


def test_delete_draft(
    client_with_login, location, minimal_record, headers, es_clear
):
    """Test draft deletion."""
    client = client_with_login
    response = client.post(
        "/records", data=json.dumps(minimal_record), headers=headers)

    assert response.status_code == 201

    recid = response.json['id']

    update_response = client.delete(
        "/records/{}/draft".format(recid), headers=headers)

    assert update_response.status_code == 204

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
    _validate_access(response.json, minimal_record)

    # Publish it
    response = client.post(
        "/records/{}/draft/actions/publish".format(recid), headers=headers)

    assert response.status_code == 202
    _assert_single_item_response(response)
    _validate_access(response.json, minimal_record)

    return recid


def test_publish_draft(
    client_with_login, location, minimal_record, headers, es_clear
):
    """Test publication of a new draft.

    It has to first create said draft.
    """
    client = client_with_login
    recid = _create_and_publish(client, minimal_record, headers)

    response = client.get(f"/records/{recid}/draft", headers=headers)
    assert response.status_code == 404

    # Check record exists
    response = client.get(f"/records/{recid}", headers=headers)

    assert 200 == response.status_code

    _assert_single_item_response(response)
    _validate_access(response.json, minimal_record)


def test_publish_draft_w_dates(
    client_with_login, location, minimal_record, headers, es_clear
):
    """Test publication of a draft with dates."""
    client = client_with_login
    dates = [{
        "date": "1939/1945",
        "type": "other",
        "description": "A date"
    }]
    minimal_record["metadata"]["dates"] = dates

    recid = _create_and_publish(client, minimal_record, headers)

    response = client.get(f"/records/{recid}/draft", headers=headers)
    assert response.status_code == 404

    # Check record exists
    response = client.get(f"/records/{recid}", headers=headers)
    assert 200 == response.status_code
    assert dates == response.json["metadata"]["dates"]


def test_user_records_and_drafts(
    client_with_login, location, headers, minimal_record, es_clear
):
    """Tests the search over the records index.

    Note: The three use cases are set in the same test so there is the
          possibility of failure. Meaning that if search is not done
          correctly more than one record/draft will be returned.
    """
    client = client_with_login
    # Create a draft
    response = client.post(
        "/records", data=json.dumps(minimal_record), headers=headers)
    assert response.status_code == 201
    draftid = response.json['id']

    RDMDraft.index.refresh()
    RDMRecord.index.refresh()

    # Search user records
    response = client.get("/user/records", headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total'] == 1
    assert response.json['hits']['hits'][0]['id'] == draftid

    # Create and publish new draft
    recid = _create_and_publish(client, minimal_record, headers)

    RDMDraft.index.refresh()
    RDMRecord.index.refresh()

    # Search user records
    response = client.get("/user/records", headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total'] == 2
    assert response.json['hits']['hits'][0]['id'] == recid
    assert response.json['hits']['hits'][1]['id'] == draftid

    # Search only for user drafts
    response = client.get("/user/records?status=draft", headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total'] == 1
    assert response.json['hits']['hits'][0]['id'] == draftid

    # Search only for user published
    response = client.get("/user/records?status=published", headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total'] == 1
    assert response.json['hits']['hits'][0]['id'] == recid

    # Edit published user's record
    response = client.post(
        "/records/{}/draft".format(recid),
        headers=headers
    )

    RDMDraft.index.refresh()
    RDMRecord.index.refresh()

    edit_recid = response.json['id']

    # Search user records
    response = client.get("/user/records", headers=headers)
    assert response.status_code == 200
    # The total results remain the same as we return the unique number of
    # user drafts and records
    assert response.json['hits']['total'] == 2

    # Search only for user drafts
    response = client.get("/user/records?status=draft", headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total'] == 2
    assert response.json['hits']['hits'][0]['id'] == edit_recid
    assert response.json['hits']['hits'][1]['id'] == draftid

    # Search only for user published
    response = client.get("/user/records?status=published", headers=headers)
    assert response.status_code == 200
    assert response.json['hits']['total'] == 0


# TODO
@pytest.mark.skip()
def test_create_publish_new_revision(
    client_with_login,
    location,
    minimal_record,
    identity_simple,
    headers,
):
    """Test draft creation of an existing record and publish it."""
    client = client_with_login
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
    assert response.json['revision_id'] == 5
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

    # TODO: Because of seting the `.bucket`/`.bucket_id` fields on the record
    # there are extra revision bumps.
    assert response.json['id'] == recid
    assert response.json['revision_id'] == 4
    assert response.json['metadata']["title"] == \
        minimal_record["metadata"]["title"]

    # Check it was actually edited
    response = client.get(
        "/records/{}".format(recid), headers=headers)

    assert response.json["metadata"]["title"] == \
        minimal_record["metadata"]["title"]


# TODO
@pytest.mark.skip()
def test_ui_data_in_record(
    app,
    client_with_login,
    location,
    minimal_record,
    headers,
    ui_headers,
):
    """Publish a record and check that it contains the UI data."""
    client = client_with_login
    recid = _create_and_publish(client, minimal_record, headers)

    RDMRecord.index.refresh()

    # Check if list results contain UI data
    response = client.get(
        '/records', query_string={'q': f'id:{recid}'}, headers=ui_headers)
    assert response.json['hits']['hits'][0]['ui']

    # Check if item results contain UI data
    response = client.get(f'/records/{recid}', headers=ui_headers)
    assert response.json['ui']
