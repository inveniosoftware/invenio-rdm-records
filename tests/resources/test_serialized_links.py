# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test RDMRecordService generated links."""

import pytest
from flask_security import login_user
from invenio_accounts.testutils import login_user_via_session

from invenio_rdm_records.records import RDMDraft, RDMRecord


@pytest.fixture
def draft_json(running_app, client, minimal_record, users, headers):
    """RDM Draft fixture."""
    login_user(users[0], remember=True)
    login_user_via_session(client, email=users[0].email)

    response = client.post("/records", json=minimal_record, headers=headers)

    RDMDraft.index.refresh()

    return response.json


@pytest.fixture
def published_json(running_app, client_with_login, minimal_record, headers):
    """RDM Record fixture.

    Can't depend on draft_json since publication deletes draft.
    """
    response = client_with_login.post("/records", json=minimal_record, headers=headers)
    pid_value = response.json["id"]
    response = client_with_login.post(
        f"/records/{pid_value}/draft/actions/publish", headers=headers
    )

    RDMRecord.index.refresh()

    return response.json


def test_draft_links(client, draft_json, minimal_record, headers):
    """Tests the links for endpoints that return a draft."""
    created_draft_links = draft_json["links"]
    pid_value = draft_json["id"]

    response = client.get(f"/records/{pid_value}/draft", headers=headers)
    read_draft_links = response.json["links"]

    expected_links = {
        "self": f"https://127.0.0.1:5000/api/records/{pid_value}/draft",
        "review": f"https://127.0.0.1:5000/api/records/{pid_value}/draft/review",  # noqa
        "self_html": f"https://127.0.0.1:5000/uploads/{pid_value}",
        "preview_html": f"https://127.0.0.1:5000/records/{pid_value}?preview=1",
        "publish": f"https://127.0.0.1:5000/api/records/{pid_value}/draft/actions/publish",  # noqa
        "record": f"https://127.0.0.1:5000/api/records/{pid_value}",
        "record_html": f"https://127.0.0.1:5000/records/{pid_value}",
        "versions": f"https://127.0.0.1:5000/api/records/{pid_value}/versions",
        "access_links": f"https://127.0.0.1:5000/api/records/{pid_value}/access/links",  # noqa
        "files": f"https://127.0.0.1:5000/api/records/{pid_value}/draft/files",
        "media_files": f"https://127.0.0.1:5000/api/records/{pid_value}/draft/media-files",
        "archive": f"https://127.0.0.1:5000/api/records/{pid_value}/draft/files-archive",  # noqa
        "archive_media": f"https://127.0.0.1:5000/api/records/{pid_value}/draft/media-files-archive",  # noqa
        "reserve_doi": f"https://127.0.0.1:5000/api/records/{pid_value}/draft/pids/doi",  # noqa
        "self_iiif_manifest": f"https://127.0.0.1:5000/api/iiif/draft:{pid_value}/manifest",  # noqa
        "self_iiif_sequence": f"https://127.0.0.1:5000/api/iiif/draft:{pid_value}/sequence/default",  # noqa
        "communities": f"https://127.0.0.1:5000/api/records/{pid_value}/communities",  # noqa
        "communities-suggestions": f"https://127.0.0.1:5000/api/records/{pid_value}/communities-suggestions",  # noqa
        "requests": f"https://127.0.0.1:5000/api/records/{pid_value}/requests",  # noqa
        "access": f"https://127.0.0.1:5000/api/records/{pid_value}/access",
        "access_request": f"https://127.0.0.1:5000/api/records/{pid_value}/access/request",
        "access_grants": f"https://127.0.0.1:5000/api/records/{pid_value}/access/grants",
        "access_users": f"https://127.0.0.1:5000/api/records/{pid_value}/access/users",
        "access_groups": f"https://127.0.0.1:5000/api/records/{pid_value}/access/groups",
    }

    assert expected_links == created_draft_links == read_draft_links


def test_record_links(client, published_json, headers):
    """Tests the links for a published RDM record."""
    pid_value = published_json["id"]
    parent_pid_value = published_json["parent"]["id"]
    doi_value = published_json["pids"]["doi"]["identifier"]
    parent_doi_value = published_json["parent"]["pids"]["doi"]["identifier"]
    published_record_links = published_json["links"]
    response = client.get(f"/records/{pid_value}", headers=headers)
    read_record_links = response.json["links"]

    expected_links = {
        "self": f"https://127.0.0.1:5000/api/records/{pid_value}",
        "self_html": f"https://127.0.0.1:5000/records/{pid_value}",
        "preview_html": f"https://127.0.0.1:5000/records/{pid_value}?preview=1",
        "doi": f"https://handle.stage.datacite.org/{doi_value}",
        "self_doi": f"https://handle.stage.datacite.org/{doi_value}",
        "self_doi_html": f"https://127.0.0.1:5000/doi/{doi_value}",
        "draft": f"https://127.0.0.1:5000/api/records/{pid_value}/draft",
        "files": f"https://127.0.0.1:5000/api/records/{pid_value}/files",
        "media_files": f"https://127.0.0.1:5000/api/records/{pid_value}/media-files",
        "archive": f"https://127.0.0.1:5000/api/records/{pid_value}/files-archive",
        "archive_media": f"https://127.0.0.1:5000/api/records/{pid_value}/media-files-archive",
        "parent": f"https://127.0.0.1:5000/api/records/{parent_pid_value}",
        "parent_html": f"https://127.0.0.1:5000/records/{parent_pid_value}",
        "parent_doi": f"https://handle.stage.datacite.org/{parent_doi_value}",
        "parent_doi_html": f"https://127.0.0.1:5000/doi/{parent_doi_value}",
        "versions": f"https://127.0.0.1:5000/api/records/{pid_value}/versions",
        "latest": f"https://127.0.0.1:5000/api/records/{pid_value}/versions/latest",  # noqa
        "latest_html": f"https://127.0.0.1:5000/records/{pid_value}/latest",  # noqa
        "access_links": f"https://127.0.0.1:5000/api/records/{pid_value}/access/links",  # noqa
        "reserve_doi": f"https://127.0.0.1:5000/api/records/{pid_value}/draft/pids/doi",  # noqa
        "self_iiif_manifest": f"https://127.0.0.1:5000/api/iiif/record:{pid_value}/manifest",  # noqa
        "self_iiif_sequence": f"https://127.0.0.1:5000/api/iiif/record:{pid_value}/sequence/default",  # noqa
        "communities": f"https://127.0.0.1:5000/api/records/{pid_value}/communities",  # noqa
        "communities-suggestions": f"https://127.0.0.1:5000/api/records/{pid_value}/communities-suggestions",  # noqa
        "requests": f"https://127.0.0.1:5000/api/records/{pid_value}/requests",  # noqa
        "access": f"https://127.0.0.1:5000/api/records/{pid_value}/access",
        "access_request": f"https://127.0.0.1:5000/api/records/{pid_value}/access/request",
        "access_grants": f"https://127.0.0.1:5000/api/records/{pid_value}/access/grants",
        "access_users": f"https://127.0.0.1:5000/api/records/{pid_value}/access/users",
        "access_groups": f"https://127.0.0.1:5000/api/records/{pid_value}/access/groups",
    }

    assert expected_links == published_record_links == read_record_links


def test_record_search_links(client, published_json, headers):
    """Tests the links for a search of published RDM records."""
    response = client.get("/records", headers=headers)
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
