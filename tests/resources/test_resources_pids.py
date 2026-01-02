# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PIDs resource level tests."""

from copy import deepcopy

import pytest


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


def publish_record(client, record, headers):
    """Publish a record."""
    draft = client.post("/records", headers=headers, json=record)
    assert draft.status_code == 201
    record = client.post(link(draft.json["links"]["publish"]), headers=headers)
    assert record.status_code == 202
    record = client.get(link(record.json["links"]["self"]), headers=headers)
    assert record.status_code == 200
    return record.json


def test_external_doi_cleanup(
    running_app, client, minimal_record, headers, search_clear, uploader
):
    """Tests for issue #845."""
    client = uploader.login(client)
    doi1 = "10.4321/1"
    doi2 = "10.4321/2"
    doi3 = "10.4321/3"

    # Publish two record with different external DOIs.
    r1_data = deepcopy(minimal_record)
    r2_data = deepcopy(minimal_record)
    r1_data["pids"] = {"doi": {"provider": "external", "identifier": doi1}}
    r2_data["pids"] = {"doi": {"provider": "external", "identifier": doi2}}
    record1 = publish_record(client, r1_data, headers)
    record2 = publish_record(client, r2_data, headers)

    def _change_doi(record, doi):
        # Edit mode
        draft = client.post(link(record["links"]["draft"]))
        assert draft.status_code == 201
        # Update
        data = draft.json
        data["pids"]["doi"]["identifier"] = doi
        res = client.put(link(draft.json["links"]["self"]), headers=headers, json=data)
        assert res.status_code == 200
        # Publish
        record = client.post(link(draft.json["links"]["publish"]), headers=headers)
        assert record.status_code == 202
        return record

    # Edit record 1 to use a DOI 3, and edit record 2 to use doi 1 (should be
    # possible because it was just released from record 1)
    record1 = _change_doi(record1, doi3)
    record2 = _change_doi(record2, doi1)


def test_external_doi_duplicate_detection(
    running_app, client, minimal_record, headers, search_clear, uploader
):
    """Tests for issue #845."""
    client = uploader.login(client)
    doi1 = "10.4321/1"

    # Publish one record with  DOIs.
    r1_data = deepcopy(minimal_record)
    r2_data = deepcopy(minimal_record)
    r1_data["pids"] = {"doi": {"provider": "external", "identifier": doi1}}
    r2_data["pids"] = {"doi": {"provider": "external", "identifier": doi1}}
    # Publish record 1 with doi 1
    record1 = publish_record(client, r1_data, headers)

    # Try to create records 2 with doi 1 - should report errors because
    # it's already assigned to another record.
    draft = client.post("/records", headers=headers, json=r2_data)
    assert draft.status_code == 201
    assert draft.json["errors"] == [
        {"field": "pids.doi", "messages": ["doi:10.4321/1 already exists."]}
    ]
    assert draft.json["pids"] == {
        "doi": {"identifier": "10.4321/1", "provider": "external"}
    }

    # Update DOI and publishing again
    data = draft.json
    data["pids"]["doi"]["identifier"] = "10.4321/2"
    res = client.put(link(draft.json["links"]["self"]), headers=headers, json=data)
    assert res.status_code == 200
    record = client.post(link(draft.json["links"]["publish"]), headers=headers)
    assert record.status_code == 202


def test_external_doi_blocked_prefix(
    running_app, client, minimal_record, headers, search_clear, uploader
):
    """Tests for issue #847."""
    client = uploader.login(client)
    # Make a DOI in the datacite prefix
    datacite_prefix = running_app.app.config["DATACITE_PREFIX"]
    doi = f"{datacite_prefix}/1"

    # Publish one record with  DOIs.
    minimal_record["pids"] = {"doi": {"provider": "external", "identifier": doi}}
    draft = client.post("/records", headers=headers, json=minimal_record)
    assert draft.status_code == 201
    # The invalid prefix should be reported.
    assert draft.json["errors"] == [
        {
            "field": "pids.doi",
            "messages": [
                "The prefix '10.1234' is managed by Invenio. Please supply an external DOI or select 'No' to have a DOI generated for you."
            ],
        }
    ]


def test_external_doi_required(
    running_app, client, minimal_record, headers, search_clear, uploader
):
    """Tests for issue #847."""
    client = uploader.login(client)
    # Create a record with no external DOI
    minimal_record["pids"] = {"doi": {"provider": "external", "identifier": ""}}
    draft = client.post("/records", headers=headers, json=minimal_record)
    assert draft.status_code == 201
    # The required identifier should be reported
    assert draft.json["errors"] == [
        {"field": "pids.doi", "messages": ["Missing DOI for required field."]}
    ]
    assert draft.json["pids"] == {"doi": {"provider": "external", "identifier": ""}}


def test_pids_publish_validation_error(
    running_app, client, minimal_record, headers, search_clear, uploader
):
    """Ensure that errors raised by Pids component at publish time serialize well."""
    client = uploader.login(client)
    del minimal_record["metadata"]["publisher"]
    draft = client.post("/records", headers=headers, json=minimal_record)

    record = client.post(link(draft.json["links"]["publish"]), headers=headers)

    assert record.status_code == 400
    expected = [
        {
            "field": "metadata.publisher",
            "messages": ["Missing publisher field required for DOI registration."],
        }
    ]
    assert expected == record.json["errors"]


def test_required_pids_removed(
    running_app, client, minimal_record, headers, search_clear, uploader
):
    """Tests that removed required PIDs are restored on publish."""
    client = uploader.login(client)
    record = publish_record(client, minimal_record, headers)
    first_publish_pids = deepcopy(record["pids"])

    # Edit
    draft = client.post(link(record["links"]["draft"]))
    assert draft.status_code == 201
    # Update to remove (required) OAI PID
    data = draft.json
    data["pids"].pop("oai")
    res = client.put(link(draft.json["links"]["self"]), headers=headers, json=data)
    assert res.status_code == 200
    # Publish
    record = client.post(link(draft.json["links"]["publish"]), headers=headers)
    assert record.status_code == 202

    # Check that the OAI PID was restored
    assert record.json["pids"] == first_publish_pids
