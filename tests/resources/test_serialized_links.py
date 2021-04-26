# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test RDMRecordService generated links."""

import pytest
from flask_security import login_user
from invenio_access.models import ActionUsers
from invenio_accounts.testutils import create_test_user, \
    login_user_via_session, login_user_via_view

HEADERS = {"content-type": "application/json", "accept": "application/json"}


@pytest.fixture
def draft_json(app, client, minimal_record, es, location, users):
    """RDM Draft fixture."""
    login_user(users[0], remember=True)
    login_user_via_session(client, email=users[0].email)

    response = client.post(
        "/records", json=minimal_record, headers=HEADERS
    )
    return response.json


@pytest.fixture
def published_json(app, client_with_login, minimal_record, es, location):
    """RDM Record fixture.

    Can't depend on draft_json since publication deletes draft.
    """
    response = client_with_login.post(
        "/records", json=minimal_record, headers=HEADERS
    )
    pid_value = response.json["id"]
    response = client_with_login.post(
        f"/records/{pid_value}/draft/actions/publish", headers=HEADERS
    )
    return response.json


def test_draft_links(client, draft_json, minimal_record):
    """Tests the links for endpoints that return a draft."""
    created_draft_links = draft_json["links"]
    pid_value = draft_json["id"]

    response = client.get(
        f"/records/{pid_value}/draft", headers=HEADERS
    )
    read_draft_links = response.json["links"]

    expected_links = {
        "self": f"https://127.0.0.1:5000/api/records/{pid_value}/draft",
        "self_html": f"https://127.0.0.1:5000/uploads/{pid_value}",
        "publish": f"https://127.0.0.1:5000/api/records/{pid_value}/draft/actions/publish",  # noqa
        "record": f"https://127.0.0.1:5000/api/records/{pid_value}",
        "versions": f"https://127.0.0.1:5000/api/records/{pid_value}/versions",
        "latest": f"https://127.0.0.1:5000/api/records/{pid_value}/versions/latest",  # noqa
        "latest_html": f"https://127.0.0.1:5000/records/{pid_value}/latest",  # noqa
        "access_links": f"https://127.0.0.1:5000/api/records/{pid_value}/access/links",  # noqa
        "files": f"https://127.0.0.1:5000/api/records/{pid_value}/draft/files",
        "reserve_doi": f"https://127.0.0.1:5000/api/records/{pid_value}/draft/pids/doi",  # noqa
    }
    assert expected_links == created_draft_links == read_draft_links


def test_record_links(client, published_json):
    """Tests the links for a published RDM record."""
    pid_value = published_json["id"]
    doi_value = published_json["pids"]["doi"]["identifier"].replace("/", "%2F")
    published_record_links = published_json["links"]
    response = client.get(f"/records/{pid_value}", headers=HEADERS)
    read_record_links = response.json["links"]

    expected_links = {
        "self": f"https://127.0.0.1:5000/api/records/{pid_value}",
        "self_html": f"https://127.0.0.1:5000/records/{pid_value}",
        "self_doi": f"https://127.0.0.1:5000/doi/{doi_value}",
        "draft": f"https://127.0.0.1:5000/api/records/{pid_value}/draft",
        "files": f"https://127.0.0.1:5000/api/records/{pid_value}/files",
        "versions": f"https://127.0.0.1:5000/api/records/{pid_value}/versions",
        "latest": f"https://127.0.0.1:5000/api/records/{pid_value}/versions/latest",  # noqa
        "latest_html": f"https://127.0.0.1:5000/records/{pid_value}/latest",  # noqa
        "access_links": f"https://127.0.0.1:5000/api/records/{pid_value}/access/links",  # noqa
        "reserve_doi": f"https://127.0.0.1:5000/api/records/{pid_value}/draft/pids/doi",  # noqa
    }
    assert expected_links == published_record_links == read_record_links


def test_record_search_links(client, published_json):
    """Tests the links for a search of published RDM records."""
    response = client.get("/records", headers=HEADERS)
    search_record_links = response.json["links"]

    expected_links = {
        # NOTE: Variations are covered in records-resources
        "self": "https://127.0.0.1:5000/api/records?page=1&size=25&sort=newest"
    }
    assert expected_links == search_record_links


def test_versions_search_links(client, published_json, headers):
    """Tests the links for a search of versions."""
    pid_value = published_json["id"]
    response = client.get(f"/records/{pid_value}/versions", headers=headers)
    search_versions_links = response.json["links"]

    expected_links = {
        "self": f"https://127.0.0.1:5000/api/records/{pid_value}/versions?page=1&size=25&sort=version"  # noqa
    }
    assert expected_links == search_versions_links
