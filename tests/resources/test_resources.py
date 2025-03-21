# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

import json
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from io import BytesIO

import arrow
import pytest
from invenio_accounts.testutils import login_user_via_session
from invenio_requests import current_requests_service
from marshmallow_utils.permissions import FieldPermissionError

from invenio_rdm_records.records import RDMDraft, RDMRecord
from invenio_rdm_records.requests import CommunitySubmission
from tests.helpers import login_user, logout_user


@pytest.fixture()
def ui_headers():
    """Default headers for making requests."""
    return {
        "content-type": "application/json",
        "accept": "application/vnd.inveniordm.v1+json",
    }


def _assert_single_item_response(response):
    """Assert the fields present on a single item response."""
    response_fields = response.json.keys()
    fields_to_check = ["access", "created", "id", "links", "metadata", "updated"]

    for field in fields_to_check:
        assert field in response_fields


def _validate_access(response, original):
    """Validate that the record's access is as specified."""
    assert "access" in response

    access, orig_access = response["access"], original["access"]
    assert access["record"] == orig_access["record"]
    assert access["files"] == orig_access["files"]

    if orig_access.get("embargo"):
        assert "embargo" in access
        embargo, orig_embargo = access["embargo"], orig_access["embargo"]

        until = arrow.get(embargo["until"]).datetime
        orig_until = arrow.get(orig_embargo["until"]).datetime
        assert until.isoformat() == orig_until.isoformat()

        if embargo.get("reason"):
            assert embargo.get("reason") == orig_embargo.get("reason")

        assert embargo.get("active") == orig_embargo.get("active")


def test_simple_flow(
    running_app, client_with_login, minimal_record, headers, search_clear
):
    """Test a simple REST API flow."""
    client = client_with_login
    # Create a draft
    created_draft = client.post(
        "/records", headers=headers, data=json.dumps(minimal_record)
    )
    assert created_draft.status_code == 201
    _assert_single_item_response(created_draft)
    _validate_access(created_draft.json, minimal_record)
    id_ = created_draft.json["id"]

    # Read the draft
    read_draft = client.get(f"/records/{id_}/draft", headers=headers)
    assert read_draft.status_code == 200
    assert read_draft.json["metadata"] == created_draft.json["metadata"]
    _validate_access(read_draft.json, minimal_record)

    # Update and save draft
    data = read_draft.json
    data["metadata"]["title"] = "New title"

    res = client.put(f"/records/{id_}/draft", headers=headers, data=json.dumps(data))
    assert res.status_code == 200
    assert res.json["metadata"]["title"] == "New title"
    _validate_access(res.json, minimal_record)

    # Publish it
    response = client.post(
        "/records/{}/draft/actions/publish".format(id_), headers=headers
    )

    # Check record was created
    recid = response.json["id"]
    response = client.get("/records/{}".format(recid), headers=headers)
    assert response.status_code == 200
    _validate_access(response.json, minimal_record)

    created_record = response.json

    RDMRecord.index.refresh()

    # Search it
    res = client.get(f"/records", query_string={"q": f"id:{recid}"}, headers=headers)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["metadata"] == created_record["metadata"]
    data = res.json["hits"]["hits"][0]
    assert data["metadata"]["title"] == "New title"
    _validate_access(data, minimal_record)


def test_create_draft(
    running_app, client_with_login, minimal_record, headers, search_clear
):
    """Test draft creation of a non-existing record."""
    client = client_with_login
    response = client.post("/records", data=json.dumps(minimal_record), headers=headers)

    assert response.status_code == 201
    _assert_single_item_response(response)
    _validate_access(response.json, minimal_record)


def test_create_partial_draft(
    running_app, client_with_login, minimal_record, headers, search_clear
):
    """Test partial draft creation of a non-existing record.

    NOTE: This tests functionality implemented in records/drafts-resources, but
          intentions specific to this module.
    """
    client = client_with_login
    minimal_record["metadata"]["title"] = ""
    response = client.post("/records", json=minimal_record, headers=headers)

    assert 201 == response.status_code
    _assert_single_item_response(response)
    errors = [
        {"field": "metadata.title", "messages": ["Shorter than minimum length 3."]},
    ]
    assert errors == response.json["errors"]


def test_create_draft_w_extra_fields_reports_error_doesnt_save_field(
    running_app, client_with_login, minimal_record, headers, search_clear
):
    """Extra fields are reported in errors but not saved."""
    client = client_with_login
    minimal_record["foo"] = "FOO!"

    response = client.post("/records", json=minimal_record, headers=headers)

    assert response.status_code == 201
    assert "foo" not in response.json


def test_read_draft(
    running_app, client_with_login, minimal_record, headers, search_clear
):
    """Test draft read."""
    client = client_with_login
    response = client.post("/records", data=json.dumps(minimal_record), headers=headers)

    assert response.status_code == 201

    recid = response.json["id"]
    response = client.get("/records/{}/draft".format(recid), headers=headers)

    assert response.status_code == 200

    _assert_single_item_response(response)
    _validate_access(response.json, minimal_record)


def test_update_draft(
    running_app, client_with_login, minimal_record, headers, search_clear
):
    """Test draft update."""
    client = client_with_login
    response = client.post("/records", data=json.dumps(minimal_record), headers=headers)

    assert response.status_code == 201
    assert response.json["metadata"]["title"] == minimal_record["metadata"]["title"]
    _validate_access(response.json, minimal_record)

    recid = response.json["id"]

    orig_title = minimal_record["metadata"]["title"]
    edited_title = "Edited title"
    minimal_record["metadata"]["title"] = edited_title

    # Update draft content
    update_response = client.put(
        "/records/{}/draft".format(recid),
        data=json.dumps(minimal_record),
        headers=headers,
    )

    assert update_response.status_code == 200
    assert update_response.json["metadata"]["title"] == edited_title
    assert update_response.json["id"] == recid
    _validate_access(update_response.json, minimal_record)

    # Check the updates were saved
    update_response = client.get("/records/{}/draft".format(recid), headers=headers)

    assert update_response.status_code == 200
    assert update_response.json["metadata"]["title"] == edited_title
    assert update_response.json["id"] == recid
    _validate_access(update_response.json, minimal_record)


def test_update_partial_draft(
    running_app, client_with_login, minimal_record, headers, search_clear
):
    """Test partial draft update.

    NOTE: This tests functionality implemented in records/drafts-resources, but
          intentions specific to this module.
    """
    client = client_with_login
    response = client.post("/records", json=minimal_record, headers=headers)
    assert 201 == response.status_code
    recid = response.json["id"]
    minimal_record["metadata"]["title"] = ""

    # Update draft content
    response = client.put(
        f"/records/{recid}/draft", json=minimal_record, headers=headers
    )

    assert 200 == response.status_code
    _assert_single_item_response(response)
    errors = [
        {"field": "metadata.title", "messages": ["Shorter than minimum length 3."]},
    ]
    assert errors == response.json["errors"]

    # The draft has had its title erased
    response = client.get(f"/records/{recid}/draft", headers=headers)
    assert 200 == response.status_code
    assert "title" not in response.json["metadata"]


def test_delete_draft(
    running_app, client_with_login, minimal_record, headers, search_clear
):
    """Test draft deletion."""
    client = client_with_login
    response = client.post("/records", data=json.dumps(minimal_record), headers=headers)

    assert response.status_code == 201

    recid = response.json["id"]

    update_response = client.delete("/records/{}/draft".format(recid), headers=headers)

    assert update_response.status_code == 204

    update_response = client.get("/records/{}/draft".format(recid), headers=headers)

    assert update_response.status_code == 404


def _create_and_publish(client, minimal_record, headers):
    """Create a draft and publish it."""
    # Create the draft
    response = client.post("/records", json=minimal_record, headers=headers)
    assert response.status_code == 201
    recid = response.json["id"]
    _validate_access(response.json, minimal_record)

    # Publish it
    response = client.post(f"/records/{recid}/draft/actions/publish", headers=headers)

    assert response.status_code == 202
    _assert_single_item_response(response)
    _validate_access(response.json, minimal_record)

    return recid


def test_publish_draft(
    running_app, client_with_login, minimal_record, headers, search_clear
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
    running_app, client_with_login, minimal_record, headers, search_clear
):
    """Test publication of a draft with dates."""
    client = client_with_login
    dates = [
        {
            "date": "1939/1945",
            "type": {"id": "other", "title": {"en": "Other"}},
            "description": "A date",
        }
    ]
    minimal_record["metadata"]["dates"] = dates

    recid = _create_and_publish(client, minimal_record, headers)

    response = client.get(f"/records/{recid}/draft", headers=headers)
    assert response.status_code == 404

    # Check record exists
    response = client.get(f"/records/{recid}", headers=headers)
    assert 200 == response.status_code
    assert dates == response.json["metadata"]["dates"]


def test_user_records_and_drafts(
    running_app, client_with_login, headers, minimal_record, search_clear
):
    """Tests the search over the drafts search alias."""
    client = client_with_login
    # Create a draft
    response = client.post("/records", data=json.dumps(minimal_record), headers=headers)
    assert response.status_code == 201
    draftid = response.json["id"]

    RDMDraft.index.refresh()
    RDMRecord.index.refresh()

    # Search user records
    response = client.get("/user/records", headers=headers)
    assert response.status_code == 200
    assert response.json["hits"]["total"] == 1
    assert response.json["hits"]["hits"][0]["id"] == draftid

    # Create and publish new draft
    recid = _create_and_publish(client, minimal_record, headers)

    RDMDraft.index.refresh()
    RDMRecord.index.refresh()

    # Search user records
    response = client.get("/user/records", headers=headers)
    assert response.status_code == 200
    assert response.json["hits"]["total"] == 2
    assert response.json["hits"]["hits"][0]["id"] == recid
    assert response.json["hits"]["hits"][1]["id"] == draftid

    # Search only for user published records and drafts
    response = client.get("/user/records?is_published=true", headers=headers)
    assert response.status_code == 200
    assert response.json["hits"]["total"] == 1
    # the published record of this draft is excluded versus the filter
    # `has_draft: False`
    assert response.json["hits"]["hits"][0]["id"] == recid

    # Search only for user new drafts
    response = client.get("/user/records?is_published=false", headers=headers)
    assert response.status_code == 200
    assert response.json["hits"]["total"] == 1
    assert response.json["hits"]["hits"][0]["id"] == draftid


def _assert_file_entry(entry, recid, filename):
    assert entry["key"] == filename

    links = entry["links"]
    assert (
        links["self"]
        == f"https://127.0.0.1:5000/api/records/{recid}/draft/files/{filename}"
    )  # noqa
    assert (
        links["content"]
        == f"https://127.0.0.1:5000/api/records/{recid}/draft/files/{filename}/content"
    )  # noqa
    assert (
        links["commit"]
        == f"https://127.0.0.1:5000/api/records/{recid}/draft/files/{filename}/commit"
    )  # noqa


def _create_and_assert_file(client, h, recid, filename, file_content):
    response = client.post(
        f"/records/{recid}/draft/files", headers=h, json=[{"key": filename}]
    )

    assert response.status_code == 201
    entries = response.json["entries"]
    found = False
    i = 0
    while not found and i < len(entries):
        entry = entries[i]
        if entry["key"] == filename:
            found = True
            _assert_file_entry(entry, recid, filename)
        i += 1

    assert found

    response = client.put(
        f"/records/{recid}/draft/files/{filename}/content",
        headers={
            "content-type": "application/octet-stream",
            "accept": "application/json",
        },
        data=BytesIO(file_content),
    )

    assert response.status_code == 200
    _assert_file_entry(entry, recid, filename)

    response = client.post(f"/records/{recid}/draft/files/{filename}/commit", headers=h)

    assert response.status_code == 200
    _assert_file_entry(entry, recid, filename)


def test_multiple_files_record(
    running_app, client_with_login, headers, minimal_record, search_clear
):
    client = client_with_login
    minimal_record["files"]["enabled"] = True
    response = client.post("/records", headers=headers, data=json.dumps(minimal_record))
    assert response.status_code == 201
    recid = response.json["id"]

    filename1 = "test.txt"
    file_content1 = b"testfile1"
    filename2 = "test2.txt"
    file_content2 = b"testfile2"

    _create_and_assert_file(client, headers, recid, filename1, file_content1)
    _create_and_assert_file(client, headers, recid, filename2, file_content2)

    response = client.post(f"/records/{recid}/draft/actions/publish", headers=headers)

    assert response.status_code == 202


@pytest.fixture()
def restricted_records_disabled(app):
    old_value = app.config.get("RDM_ALLOW_RESTRICTED_RECORDS", True)
    app.config["RDM_ALLOW_RESTRICTED_RECORDS"] = False
    yield
    app.config["RDM_ALLOW_RESTRICTED_RECORDS"] = old_value


def test_restricted_records_disabled(
    running_app,
    client_with_login,
    headers,
    minimal_record,
    search_clear,
    superuser,
    restricted_records_disabled,
):
    client = client_with_login
    response = client.post("/records", json=minimal_record, headers=headers)
    recid = response.json["id"]

    assert response.status_code == 201
    assert response.json["access"]["record"] == "public"

    # Trying to change record access to restricted will fail
    minimal_record["access"]["record"] = "restricted"
    response = client.put(
        f"/records/{recid}/draft",
        json=minimal_record,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json["errors"][0]["field"] == "access"
    assert response.json["errors"][0]["messages"] == [
        "You don't have permissions to manage record access.",
    ]
    # Record access should still be "public"
    response = client.get(f"/records/{recid}/draft", headers=headers)
    assert response.json["access"]["record"] == "public"

    # Superuser can change record access
    superuser.login(client, logout_first=True)
    minimal_record["access"]["record"] = "restricted"
    response = client.put(
        f"/records/{recid}/draft",
        json=minimal_record,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json["access"]["record"] == "restricted"
    assert "errors" not in response.json


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

    # Create new draft of said record
    orig_title = minimal_record["metadata"]["title"]
    minimal_record["metadata"]["title"] = "Edited title"

    response = client.post("/records/{}/draft".format(recid), headers=headers)

    assert response.status_code == 201
    assert response.json["revision_id"] == 5
    _assert_single_item_response(response)

    # Update that new draft
    response = client.put(
        "/records/{}/draft".format(recid),
        data=json.dumps(minimal_record),
        headers=headers,
    )

    assert response.status_code == 200

    # Check the actual record was not modified
    response = client.get("/records/{}".format(recid), headers=headers)

    assert response.status_code == 200
    _assert_single_item_response(response)
    assert response.json["metadata"]["title"] == orig_title

    # Publish it to check the increment in reversion
    response = client.post(
        "/records/{}/draft/actions/publish".format(recid), headers=headers
    )

    assert response.status_code == 202
    _assert_single_item_response(response)

    # TODO: Because of seting the `.bucket`/`.bucket_id` fields on the record
    # there are extra revision bumps.
    assert response.json["id"] == recid
    assert response.json["revision_id"] == 4
    assert response.json["metadata"]["title"] == minimal_record["metadata"]["title"]

    # Check it was actually edited
    response = client.get("/records/{}".format(recid), headers=headers)

    assert response.json["metadata"]["title"] == minimal_record["metadata"]["title"]


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
        "/records", query_string={"q": f"id:{recid}"}, headers=ui_headers
    )
    assert response.json["hits"]["hits"][0]["ui"]

    # Check if item results contain UI data
    response = client.get(f"/records/{recid}", headers=ui_headers)
    assert response.json["ui"]


#
# Links Endpoint
#


def test_link_creation(
    running_app,
    client_with_login,
    minimal_record,
    headers,
    search_clear,
):
    """Test the creation of secret links."""
    client = client_with_login
    in_10_days = datetime.utcnow() + timedelta(days=10)
    in_10_days_str = in_10_days.strftime("%Y-%m-%d")

    # Create and publish a draft
    recid = _create_and_publish(client, minimal_record, headers)

    # check that there are no links yet (and the endpoint works)
    links_result = client.get(f"/records/{recid}/access/links", headers=headers)
    assert links_result.status_code == 200
    assert int(links_result.json["hits"]["total"]) == 0
    assert len(links_result.json["hits"]["hits"]) == 0

    # create a secret link
    link_result = client.post(
        f"/records/{recid}/access/links",
        headers=headers,
        data=json.dumps({"permission": "view"}),
    )

    assert link_result.status_code == 201
    link_id = link_result.json["id"]
    link_json = link_result.json

    assert link_json["id"]
    assert link_json["permission"] == "view"
    assert link_json["token"]
    assert link_json["created_at"]
    assert not link_json.get("expires_at")

    # check that the created link is findable
    links_result = client.get(f"/records/{recid}/access/links", headers=headers)
    assert links_result.status_code == 200
    assert int(links_result.json["hits"]["total"]) == 1
    assert len(links_result.json["hits"]["hits"]) == 1

    new_link_result = client.get(
        f"/records/{recid}/access/links/{link_id}", headers=headers
    )
    new_link_json = new_link_result.json
    assert new_link_result.status_code == 200
    assert new_link_json["id"] == link_id
    assert new_link_json["token"] == link_json["token"]
    assert new_link_json["permission"] == link_json["permission"]
    assert new_link_json["created_at"] == link_json["created_at"]
    assert not new_link_json.get("expires_at")

    # create an expiring link
    link_result = client.post(
        f"/records/{recid}/access/links",
        headers=headers,
        data=json.dumps({"permission": "preview", "expires_at": in_10_days_str}),
    )

    link_json = link_result.json
    assert link_result.status_code == 201
    assert link_json["id"]
    assert link_json["permission"] == "preview"
    assert link_json["token"]
    assert link_json["created_at"]
    assert link_json["expires_at"]

    # check that both links exist
    links_result = client.get(f"/records/{recid}/access/links", headers=headers)
    assert links_result.status_code == 200
    assert int(links_result.json["hits"]["total"]) == 2
    assert len(links_result.json["hits"]["hits"]) == 2


def test_link_deletion(
    running_app, client_with_login, minimal_record, headers, search_clear
):
    """Test the deletion of a secret link."""
    client = client_with_login

    # Create and publish a draft
    recid = _create_and_publish(client, minimal_record, headers)

    # create a link and delete it again
    link_result = client.post(
        f"/records/{recid}/access/links",
        headers=headers,
        data=json.dumps({"permission": "view"}),
    )
    link_id = link_result.json["id"]

    # check that the record exists
    link_result = client.get(
        f"/records/{recid}/access/links/{link_id}", headers=headers
    )
    assert link_result.status_code == 200

    # delete the record
    delete_result = client.delete(
        f"/records/{recid}/access/links/{link_id}", headers=headers
    )
    assert delete_result.status_code == 204

    # check that the record is deleted
    link_result = client.get(
        f"/records/{recid}/access/links/{link_id}", headers=headers
    )
    assert link_result.status_code == 404

    # check that there are no links left
    links_result = client.get(f"/records/{recid}/access/links", headers=headers)
    assert links_result.status_code == 200
    assert int(links_result.json["hits"]["total"]) == 0
    assert len(links_result.json["hits"]["hits"]) == 0


def test_link_update(
    running_app, client_with_login, minimal_record, headers, search_clear
):
    """Test the deletion of a secret link."""
    client = client_with_login
    # Note, we test with and without timezone aware timestamps.
    in_10_days = datetime.utcnow() + timedelta(days=10)
    in_10_days_str = in_10_days.replace(tzinfo=timezone.utc).strftime("%Y-%m-%d")
    in_20_days = arrow.utcnow() + timedelta(days=20)
    in_20_days_str = in_20_days.strftime("%Y-%m-%d")
    _10_days_ago = datetime.utcnow() - timedelta(days=10)
    _10_days_ago_str = _10_days_ago.strftime("%Y-%m-%d")

    # Create and publish a draft
    recid = _create_and_publish(client, minimal_record, headers)

    # create a link and delete it again
    link_result = client.post(
        f"/records/{recid}/access/links",
        headers=headers,
        data=json.dumps({"permission": "view"}),
    )
    link_id = link_result.json["id"]

    # reducing the lifespan of a link should work...
    link_result = client.patch(
        f"/records/{recid}/access/links/{link_id}",
        headers=headers,
        data=json.dumps({"expires_at": in_10_days_str}),
    )
    assert link_result.status_code == 200
    assert link_result.json["expires_at"] == in_10_days_str

    # ... but extending the lifespan shouldn't work
    link_result = client.patch(
        f"/records/{recid}/access/links/{link_id}",
        headers=headers,
        data=json.dumps({"expires_at": in_20_days_str}),
    )
    assert link_result.status_code == 400

    # also, past dates shouldn't work either
    link_result = client.patch(
        f"/records/{recid}/access/links/{link_id}",
        headers=headers,
        data=json.dumps({"expires_at": _10_days_ago_str}),
    )
    assert link_result.status_code == 400

    # permission level update should work fine
    link_result = client.patch(
        f"/records/{recid}/access/links/{link_id}",
        headers=headers,
        data=json.dumps({"permission": "preview"}),
    )
    assert link_result.status_code == 200
    assert link_result.json["expires_at"] == in_10_days_str
    assert link_result.json["permission"] == "preview"


def test_response_handlers(running_app, minimal_record, client_with_login):
    """Test that all configured response handlers succeed on item and search."""
    # Check that the response handlers are correctly configured.
    # The correctness of its serialization is tested in /tests/serializers

    accept = [
        "application/json",
        "application/marcxml+xml",
        "application/vnd.inveniordm.v1+json",
        "application/vnd.citationstyles.csl+json",
        "application/vnd.datacite.datacite+json",
        "application/vnd.geo+json",
        "application/vnd.datacite.datacite+xml",
        "application/x-dc+xml",
        "text/x-bibliography",
        "application/dcat+xml",
        "application/linkset+json",
    ]

    headers = {
        "content-type": "application/json",
        "accept": "application/json",
    }
    client = client_with_login
    recid = _create_and_publish(client, minimal_record, headers)
    RDMRecord.index.refresh()

    for format in accept:
        headers["accept"] = format
        assert (
            200 == client.get("/records/{}".format(recid), headers=headers).status_code
        )

        assert 200 == client.get(f"/records", headers=headers).status_code


#
# DOI API
#


def test_reserve_pid_with_login(
    running_app, client_with_login, minimal_record, headers, search_clear
):
    """Test the reserve function with client logged in."""
    # GET with client login
    client = client_with_login
    # Create the draft
    response = client.post("/records", data=json.dumps(minimal_record), headers=headers)

    assert response.status_code == 201
    recid = response.json["id"]

    response = client.post(f"/records/{recid}/draft/pids/doi", headers=headers)
    assert response.status_code == 201
    assert response.json["pids"]["doi"]["identifier"]


def test_discard_pid_with_login(
    running_app, client_with_login, minimal_record, headers, search_clear
):
    """Test the discard function."""
    # GET with client login
    client = client_with_login
    # Create the draft
    response = client.post("/records", data=json.dumps(minimal_record), headers=headers)

    assert response.status_code == 201
    recid = response.json["id"]

    # reserve a doi
    response = client.post(f"/records/{recid}/draft/pids/doi", headers=headers)
    assert response.status_code == 201
    assert response.json["pids"]["doi"]["identifier"]

    # remove the doi
    pids = response.json["pids"]
    pids.pop("doi")
    response = client.delete(f"/records/{recid}/draft/pids/doi", headers=headers)
    assert response.status_code == 200
    assert response.json["pids"] == {}


def test_publish_pid_flow(
    running_app, client_with_login, minimal_record, headers, search_clear
):
    """Test the reserve function with client logged in."""
    # GET with client login
    client = client_with_login
    # Create the draft
    response = client.post("/records", data=json.dumps(minimal_record), headers=headers)

    assert response.status_code == 201
    recid = response.json["id"]

    # Reserve DOI
    response = client.post(f"/records/{recid}/draft/pids/doi", headers=headers)
    assert response.status_code == 201
    assert response.json["pids"]["doi"]["identifier"]
    assert response.json["pids"]["doi"]["client"] == "datacite"  # default

    # Publish it, will register DOI
    response = client.post(f"/records/{recid}/draft/actions/publish", headers=headers)
    assert response.status_code == 202
    assert response.json["pids"]["doi"]["identifier"]
    assert response.json["pids"]["doi"]["client"] == "datacite"  # default


def test_search_community_records(
    running_app,
    client,
    client_with_login,
    minimal_record,
    headers,
    community,
    search_clear,
):
    """Test searching for records in a community."""
    superuser_identity = running_app.superuser_identity

    def _create_and_include_in_community():
        """Create a draft and include it in a community."""
        _client = client_with_login
        # Create the draft with review
        review = {
            "parent": {
                "review": {
                    "type": CommunitySubmission.type_id,
                    "receiver": {"community": community["id"]},
                }
            }
        }
        resp = _client.post(
            "/records", json={**minimal_record, **review}, headers=headers
        )
        assert resp.status_code == 201
        recid = resp.json["id"]

        # Submit for review
        resp = _client.post(
            f"/records/{recid}/draft/actions/submit-review", headers=headers
        )
        assert resp.status_code == 202
        reqid = resp.json["id"]

        # Accept the request
        current_requests_service.execute_action(superuser_identity, reqid, "accept", {})
        RDMRecord.index.refresh()

    res = client.get(
        f"/communities/abcdef/records", headers=headers
    )  # Random ID -> should return 404 Not Found
    assert res.status_code == 404

    res = client.get(
        f"/communities/{community['id']}/records", headers=headers
    )  # Valid ID should return 200 with a number of total hits = 0
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 0

    _create_and_include_in_community()

    res = client.get(f"/communities/{community['id']}/records", headers=headers)
    assert res.json["hits"]["total"] == 1


def test_search_internal_notes_fields(
    running_app, client, minimal_record, headers, search_clear, superuser, users
):

    # login regular user
    login_user(client, users[0])
    minimal_record_w_int_notes = deepcopy(minimal_record)
    minimal_record_w_int_notes["internal_notes"] = [{"note": "abc"}]

    with pytest.raises(FieldPermissionError):
        resp = client.post(
            "/records", json={**minimal_record_w_int_notes}, headers=headers
        )

    # login admin
    logout_user(client)
    user = superuser.user
    login_user(client, user)

    resp = client.post("/records", json={**minimal_record_w_int_notes}, headers=headers)
    assert resp.status_code == 201

    recid = resp.json["id"]
    response = client.post(
        "/records/{}/draft/actions/publish".format(recid), headers=headers
    )

    resp = client.get(f"/records/{recid}")
    assert resp.json["id"] == recid
    assert resp.json["internal_notes"][0]["note"] == "abc"
    resp = client.get("/records?q=abc")
    assert resp.json["hits"]["total"] == 0
    resp = client.get("/records?q=internal_notes.note:abc")
    assert resp.json["hits"]["total"] == 1

    # login user to check search and field perms
    logout_user(client)
    login_user(client, users[0])

    resp = client.get(f"/records/{recid}")
    assert "internal_notes" not in resp.json

    resp = client.get("/records?q=abc")
    assert resp.json["hits"]["total"] == 0
    resp = client.get("/records?q=internal_notes.note:abc")
    assert resp.json["hits"]["total"] == 0
    logout_user(client)
