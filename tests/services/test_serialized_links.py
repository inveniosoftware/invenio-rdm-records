# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test BibliographicRecordService generated links."""

import pytest
from invenio_access.models import ActionUsers
from invenio_accounts.testutils import create_test_user, login_user_via_view

from invenio_rdm_records.services import BibliographicRecordService

HEADERS = {"content-type": "application/json", "accept": "application/json"}


@pytest.fixture
def draft_json(app, client, minimal_record, es):
    """Bibliographic Draft fixture."""
    response = client.post(
        "/records", json=minimal_record, headers=HEADERS
    )
    return response.json


@pytest.fixture
def published_json(app, client, minimal_record, es):
    """Bibliographic Record fixture.

    Can't depend on draft_json since publication deletes draft.
    """
    response = client.post(
        "/records", json=minimal_record, headers=HEADERS
    )
    pid_value = response.json["id"]
    response = client.post(
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
        "self": f"https://localhost:5000/api/records/{pid_value}/draft",
        "self_html": f"https://localhost:5000/uploads/{pid_value}",
        "publish": f"https://localhost:5000/api/records/{pid_value}/draft/actions/publish",  # noqa
        # TODO: Uncomment when files can be associated with drafts
        # "files": f"https://localhost:5000/api/records/{pid_value}/files",
    }
    assert expected_links == created_draft_links == read_draft_links


def test_record_links(client, published_json):
    """Tests the links for a published bibliographic record."""
    pid_value = published_json["id"]
    published_record_links = published_json["links"]
    response = client.get(f"/records/{pid_value}", headers=HEADERS)
    read_record_links = response.json["links"]

    expected_links = {
        "self": f"https://localhost:5000/api/records/{pid_value}",
        "self_html": f"https://localhost:5000/records/{pid_value}",
        # "edit": f"https://localhost:5000/api/records/{pid_value}/draft",
        # "files": f"https://localhost:5000/api/records/{pid_value}/files",
        # TODO: Uncomment when implemented
        # "versions":
        #   f"https://localhost:5000/api/records/{pid_value}/...",
        # "latest": f"https://localhost:5000/api/records/{pid_value}/...",
    }
    assert expected_links == published_record_links == read_record_links


def test_record_search_links(client, published_json):
    """Tests the links for a search of published bibliographic records."""
    response = client.get("/records", headers=HEADERS)
    search_record_links = response.json["links"]

    expected_links = {
        # NOTE: Variations are covered in records-resources
        "self": "https://localhost:5000/api/records?page=1&size=25&sort=newest"
    }
    assert expected_links == search_record_links


@pytest.mark.skip()
def test_permission_links(client, db, published_json):
    """Test the links when affected by permissions."""
    # We test that only admins get the "delete" link (according to our policy)
    pid_value = published_json["id"]
    user = create_test_user("jane@example.com")
    db.session.add(ActionUsers(action='admin-access', user=user))
    db.session.commit()
    login_user_via_view(
        client, email=user.email, password=user.password_plaintext,
        login_url='/login'
    )
    response = client.get(f"/records/{pid_value}", headers=HEADERS)
    read_record_links = response.json["links"]

    assert (
        f"https://localhost:5000/api/records/{pid_value}" ==
        read_record_links["delete"]
    )
