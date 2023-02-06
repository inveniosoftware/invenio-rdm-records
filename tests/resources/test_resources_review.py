# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

import json

import pytest
from invenio_communities import current_communities
from invenio_communities.communities.records.api import Community
from invenio_requests.records.api import RequestEvent

from invenio_rdm_records.records import RDMRecord


def link(url):
    """Strip the host part of a link."""
    api_prefix = "https://127.0.0.1:5000/api"
    if url.startswith(api_prefix):
        return url[len(api_prefix) :]


@pytest.fixture()
def ui_headers():
    """Default headers for making requests."""
    return {
        "content-type": "application/json",
        "accept": "application/vnd.inveniordm.v1+json",
    }


def test_simple_flow(
    running_app,
    client,
    minimal_record,
    community,
    headers,
    search_clear,
    curator,
    uploader,
):
    """Test a simple REST API flow."""
    client = uploader.login(client)

    # Request a review
    minimal_record["parent"] = {
        "review": {
            "type": "community-submission",
            "receiver": {"community": community.data["id"]},
        }
    }

    # # Create a draft
    draft = client.post("/records", headers=headers, data=json.dumps(minimal_record))
    links = draft.json["links"]
    review = draft.json["parent"]["review"]
    assert draft.status_code == 201
    assert "submit-review" in links
    assert "id" in review
    assert review["receiver"] == {"community": community.data["id"]}
    assert review["type"] == "community-submission"
    assert draft.json["parent"]["communities"] == {}

    # Submit for review
    comment = {"payload": {"content": "What do you think?", "format": "html"}}
    req = client.post(link(links["submit-review"]), json=comment, headers=headers)
    assert req.status_code == 202
    assert req.json["status"] == "submitted"
    assert req.json["is_open"] is True
    assert req.json["title"] == minimal_record["metadata"]["title"]
    assert req.json["created_by"] == {"user": str(uploader.id)}
    assert req.json["topic"] == {"record": draft.json["id"]}
    assert req.json["receiver"] == {"community": community.data["id"]}
    assert "number" in req.json

    # Read timeline
    RequestEvent.index.refresh()
    timeline = client.get(link(req.json["links"]["timeline"]), headers=headers)
    assert timeline.status_code == 200
    assert timeline.json["hits"]["total"] == 1

    # Accept request
    client = curator.login(client, logout_first=True)
    req = client.get(link(req.json["links"]["self"]), headers=headers)

    comment = {"payload": {"content": "Awesome stuff", "format": "html"}}
    accept_link = link(req.json["links"]["actions"]["accept"])
    req = client.post(accept_link, json=comment, headers=headers)
    assert req.status_code == 200  # TODO: should be 202?
    assert req.json["status"] == "accepted"
    assert req.json["is_open"] is False

    # Read timeline
    client = uploader.login(client, logout_first=True)

    RequestEvent.index.refresh()
    timeline_link = link("{}/timeline".format(req.json["links"]["self"]))
    timeline = client.get(timeline_link, headers=headers)
    assert timeline.status_code == 200
    # submit comment + accept log event + accept comment
    assert timeline.json["hits"]["total"] == 3

    # Read it - and assert community membership and publication status
    record = client.get(link(links["record"]), headers=headers)
    assert record.status_code == 200
    assert record.json["is_published"] is True
    assert "review" not in record.json["parent"]
    comms = record.json["parent"]["communities"]
    assert comms["ids"] == [community.data["id"]]
    assert comms["default"] == community.data["id"]
    comm_id = comms["default"]

    RDMRecord.index.refresh()

    # Search it
    res = client.get(
        f"/records",
        query_string={"q": f"parent.communities.ids:{comm_id}"},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1


def test_review_endpoints(
    running_app,
    client,
    minimal_record,
    community,
    headers,
    search_clear,
    curator,
    uploader,
    community2,
):
    """Test a simple REST API flow."""
    # Create draft
    client = uploader.login(client)
    draft = client.post("/records", headers=headers, json=minimal_record)
    assert draft.status_code == 201
    links = draft.json["links"]

    # Create the review
    review_link = link(links["review"])
    review = {
        "type": "community-submission",
        "receiver": {"community": community.data["id"]},
    }
    req = client.put(review_link, headers=headers, json=review)
    assert req.status_code == 200
    assert req.json["status"] == "created"
    assert req.json["is_open"] is False
    assert req.json["is_closed"] is False
    assert req.json["created_by"] == {"user": str(uploader.id)}
    assert req.json["topic"] == {"record": draft.json["id"]}
    assert req.json["receiver"] == {"community": community.data["id"]}
    assert "number" in req.json

    # Update to another review
    review = {
        "type": "community-submission",
        "receiver": {"community": community2.data["id"]},
    }
    req = client.put(review_link, headers=headers, json=review)
    assert req.status_code == 200
    assert req.json["receiver"] == {"community": community2.data["id"]}

    # Delete the review
    req = client.delete(review_link, headers=headers)
    assert req.status_code == 204

    # Read draft
    draft = client.get(link(links["self"]), headers=headers)
    assert draft.status_code == 200
    assert "review" not in draft.json["parent"]


def test_review_errors(
    running_app,
    client,
    minimal_record,
    community,
    headers,
    search_clear,
    curator,
    uploader,
):
    client = uploader.login(client)

    # Invalid request type
    minimal_record["parent"] = {
        "review": {"type": "invalid", "receiver": {"community": community.data["id"]}}
    }
    draft = client.post("/records", headers=headers, json=minimal_record)
    assert draft.status_code == 400


def test_delete_no_review(
    running_app,
    client,
    minimal_record,
    community,
    headers,
    search_clear,
    curator,
    uploader,
):
    """."""
    # Create draft
    client = uploader.login(client)
    draft = client.post("/records", headers=headers, json=minimal_record)
    assert draft.status_code == 201
    links = draft.json["links"]

    # Try to delete - should not be possible because it does not exists
    review_link = link(links["review"])
    req = client.delete(review_link, headers=headers)
    assert req.status_code == 404

    # Create the review and submit
    review = {
        "type": "community-submission",
        "receiver": {"community": community.data["id"]},
    }
    req = client.put(review_link, headers=headers, json=review)
    assert req.status_code == 200
    req = client.post(f"{link(links['self'])}/actions/submit-review", headers=headers)
    assert req.status_code == 202

    # Try to delete an open review - should not be possible
    req = client.delete(review_link, headers=headers)
    assert req.status_code == 400
