# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test some permissions on RDMRecordFilesResource.

Not every case is tested, but enough high-level ones for it to be useful.
"""

from io import BytesIO

import pytest

from tests.helpers import login_user, logout_user


def create_draft(client, record, headers):
    """Create draft ready for file attachment and return its id."""
    record["files"] = {"enabled": True}
    response = client.post("/records", json=record, headers=headers)
    assert response.status_code == 201
    return response.json["id"]


def init_file(client, recid, headers):
    """Init a file for draft with given recid."""
    return client.post(
        f"/records/{recid}/draft/files", headers=headers, json=[{"key": "test.pdf"}]
    )


def upload_file(client, recid):
    """Create draft and return its id."""
    return client.put(
        f"/records/{recid}/draft/files/test.pdf/content",
        headers={
            "content-type": "application/octet-stream",
            "accept": "application/json",
        },
        data=BytesIO(b"testfile"),
    )


def commit_file(client, recid, headers):
    """Create draft and return its id."""
    return client.post(f"/records/{recid}/draft/files/test.pdf/commit", headers=headers)


def test_only_owners_can_init_file_upload(
    client, headers, running_app, minimal_record, users
):
    login_user(client, users[0])

    recid = create_draft(client, minimal_record, headers)

    # Anonymous user can't init file for it
    logout_user(client)
    response = init_file(client, recid, headers)
    assert response.status_code == 403

    # Different user can't init file for it
    login_user(client, users[1])
    response = init_file(client, recid, headers)
    assert response.status_code == 403

    # Owner can init file for it
    logout_user(client)
    login_user(client, users[0])
    response = init_file(client, recid, headers)
    assert response.status_code == 201


def test_only_owners_can_upload_file(
    client, headers, running_app, minimal_record, users
):
    login_user(client, users[0])

    recid = create_draft(client, minimal_record, headers)
    init_file(client, recid, headers)

    # Anonymous user
    logout_user(client)
    response = upload_file(client, recid)
    assert response.status_code == 403

    # Different user
    login_user(client, users[1])
    response = upload_file(client, recid)
    assert response.status_code == 403

    # Owner
    logout_user(client)
    login_user(client, users[0])
    response = upload_file(client, recid)
    assert response.status_code == 200


def test_only_owners_can_commit_file(
    client, headers, running_app, minimal_record, users
):
    login_user(client, users[0])

    recid = create_draft(client, minimal_record, headers)
    init_file(client, recid, headers)
    upload_file(client, recid)

    # Anonymous user
    logout_user(client)
    response = commit_file(client, recid, headers)
    assert response.status_code == 403

    # Different user
    login_user(client, users[1])
    response = commit_file(client, recid, headers)
    assert response.status_code == 403

    # Owner
    logout_user(client)
    login_user(client, users[0])
    response = commit_file(client, recid, headers)
    assert response.status_code == 200


def create_draft_w_file(client, record, headers):
    """Create record with a file."""
    recid = create_draft(client, record, headers)
    response = init_file(client, recid, headers)
    assert response.status_code == 201
    response = upload_file(client, recid)
    assert response.status_code == 200
    response = commit_file(client, recid, headers)
    assert response.status_code == 200
    return recid


@pytest.fixture(scope="function")
def draft_w_restricted_file(client, headers, running_app, minimal_record, users):
    # Login
    login_user(client, users[0])

    # NOTE: This covers all scenarios of file restriction.
    #       (e.g. restricted record has its files restricted too)
    restricted_files_record = minimal_record
    restricted_files_record["access"]["files"] = "restricted"

    recid = create_draft_w_file(client, restricted_files_record, headers)

    # Logout
    logout_user(client)

    return recid


@pytest.fixture(scope="function")
def draft_w_public_file(client, headers, running_app, minimal_record, users):
    # Login
    login_user(client, users[0])

    # NOTE: minimal_record has public files by default
    recid = create_draft_w_file(client, minimal_record, headers)

    # Logout
    logout_user(client)

    return recid


def test_only_owners_can_list_restricted_files(
    client, headers, draft_w_restricted_file, users
):
    recid = draft_w_restricted_file
    url = f"/records/{recid}/draft/files"

    # Anonymous user can't list files
    response = client.get(url, headers=headers)
    assert response.status_code == 403

    # Different user can't list files
    login_user(client, users[1])
    response = client.get(url, headers=headers)
    assert response.status_code == 403

    # Owner can list files
    logout_user(client)
    login_user(client, users[0])
    response = client.get(url, headers=headers)
    assert response.status_code == 200


def test_only_owners_can_read_restricted_file_metadata(
    client, headers, draft_w_restricted_file, users
):
    recid = draft_w_restricted_file
    url = f"/records/{recid}/draft/files/test.pdf"

    # Anonymous user can't read file metadata
    response = client.get(url, headers=headers)
    assert response.status_code == 403

    # Different user can't read file metadata
    login_user(client, users[1])
    response = client.get(url, headers=headers)
    assert response.status_code == 403

    # Owner can read file metadata
    logout_user(client)
    login_user(client, users[0])
    response = client.get(url, headers=headers)
    assert response.status_code == 200


def test_only_owners_can_download_restricted_file(
    client, headers, draft_w_restricted_file, users
):
    recid = draft_w_restricted_file
    url = f"/records/{recid}/draft/files/test.pdf/content"

    # Anonymous user can't download file
    response = client.get(url, headers=headers)
    assert response.status_code == 403

    # Different user can't download file
    login_user(client, users[1])
    response = client.get(url, headers=headers)
    assert response.status_code == 403

    # Owner can download file
    logout_user(client)
    login_user(client, users[0])
    response = client.get(url, headers=headers)
    assert response.status_code == 200


def test_only_owners_can_import_files(client, headers, draft_w_public_file, users):
    recid = draft_w_public_file

    # Login with owner and publish draft with files
    login_user(client, users[0])
    response = client.post(f"/records/{recid}/draft/actions/publish", headers=headers)
    assert response.status_code == 202
    assert response.json["id"] == recid
    assert response.json["is_published"] is True
    assert response.json["versions"]["index"] == 1

    # Create new draft from the published record
    response = client.post(f"/records/{recid}/versions", headers=headers)
    assert response.status_code == 201
    assert response.json["is_published"] is False
    assert response.json["versions"]["index"] == 2
    draft_id = response.json["id"]
    logout_user(client)

    url = f"/records/{draft_id}/draft/actions/files-import"

    # Anonymous user can't import files from parent record
    response = client.post(url, headers=headers)
    assert response.status_code == 403

    # Different user can't import files from parent record
    login_user(client, users[1])
    response = client.post(url, headers=headers)
    assert response.status_code == 403
    logout_user(client)

    # Owner can import files from parent record
    login_user(client, users[0])
    response = client.post(url, headers=headers)
    assert response.status_code == 201
    assert response.json["entries"][0]["key"] == "test.pdf"

    # Double check if files are copied from the parent record
    response = client.get(f"/records/{draft_id}/draft/files", headers=headers)
    assert response.status_code == 200
    assert response.json["entries"][0]["key"] == "test.pdf"


def test_only_owners_can_delete_file(client, headers, draft_w_public_file, users):
    recid = draft_w_public_file
    url = f"/records/{recid}/draft/files/test.pdf"

    # Anonymous user can't delete file
    response = client.delete(url, headers=headers)
    assert response.status_code == 403

    # Different user can't delete file
    login_user(client, users[1])
    response = client.delete(url, headers=headers)
    assert response.status_code == 403

    # Owner can delete file
    logout_user(client)
    login_user(client, users[0])
    response = client.delete(url, headers=headers)
    assert response.status_code == 204


def test_only_owners_can_delete_all_files(client, headers, draft_w_public_file, users):
    recid = draft_w_public_file
    url = f"/records/{recid}/draft/files"

    # Anonymous user can't delete all files
    response = client.delete(url, headers=headers)
    assert response.status_code == 403

    # Different user can't delete all files
    login_user(client, users[1])
    response = client.delete(url, headers=headers)
    assert response.status_code == 403

    # Owner can delete all files
    logout_user(client)
    login_user(client, users[0])
    response = client.delete(url, headers=headers)
    assert response.status_code == 204


def test_only_owners_can_update_file_options(
    client, headers, draft_w_public_file, minimal_record, users
):
    recid = draft_w_public_file
    url = f"/records/{recid}/draft"
    minimal_record["files"] = {
        "enabled": True,
        "default_preview": "test.pdf",
    }

    # Anonymous user can't update file options
    response = client.put(url, json=minimal_record, headers=headers)
    assert response.status_code == 403

    # Different user can't update file options
    login_user(client, users[1])
    response = client.put(url, json=minimal_record, headers=headers)
    assert response.status_code == 403

    # Owner can update file options
    logout_user(client)
    login_user(client, users[0])
    response = client.put(url, json=minimal_record, headers=headers)
    assert response.status_code == 200
    assert "test.pdf" == response.json["files"]["default_preview"]


def test_only_owners_can_list_draft_w_public_files(
    client, headers, draft_w_public_file, users
):
    # Indeed drafts should only be seen by their owners (+ shared with soon)
    recid = draft_w_public_file
    url = f"/records/{recid}/draft/files"

    # Anonymous user can't list files
    response = client.get(url, headers=headers)
    assert 403 == response.status_code

    # Different user can't list files
    login_user(client, users[1])
    response = client.get(url, headers=headers)
    assert 403 == response.status_code

    # Owner can list files
    logout_user(client)
    login_user(client, users[0])
    response = client.get(url, headers=headers)
    assert 200 == response.status_code


@pytest.fixture()
def metadata_only_records_disabled(app):
    old_value = app.config.get("RDM_ALLOW_METADATA_ONLY_RECORDS", True)
    app.config["RDM_ALLOW_METADATA_ONLY_RECORDS"] = False
    yield
    app.config["RDM_ALLOW_METADATA_ONLY_RECORDS"] = old_value


def test_metadata_only_records_disabled(
    client,
    headers,
    minimal_record,
    users,
    superuser,
    metadata_only_records_disabled,
):
    login_user(client, users[0])

    recid = create_draft(client, minimal_record, headers)
    url = f"/records/{recid}/draft"
    minimal_record["files"] = {"enabled": False}

    # Owner can't disable files
    response = client.put(url, json=minimal_record, headers=headers)
    assert response.status_code == 200
    assert response.json["files"]["enabled"] is True
    assert response.json["errors"][0]["field"] == "files.enabled"
    assert response.json["errors"][0]["messages"] == [
        "You don't have permissions to manage files options.",
    ]

    # Admins though can disable files
    logout_user(client)
    login_user(client, superuser.user)
    response = client.put(url, json=minimal_record, headers=headers)
    assert response.status_code == 200
    assert response.json["files"]["enabled"] is False
    assert "errors" not in response.json
