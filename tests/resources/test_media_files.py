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
    record["media_files"] = {"enabled": True}
    response = client.post("/records", json=record, headers=headers)
    assert response.status_code == 201
    return response.json["id"]


def publish_draft(client, recid, headers):
    """Publish a draft and returns the id."""
    response = client.post(f"/records/{recid}/draft/actions/publish", headers=headers)
    assert response.status_code == 202
    assert response.data
    return recid


def delete_record(client, recid, headers):
    """Soft delete a record."""
    response = client.delete(f"/records/{recid}/delete", json={}, headers=headers)
    assert response.status_code == 204
    response.close()


def init_file(client, recid, headers):
    """Init a file for draft with given recid."""
    return client.post(
        f"/records/{recid}/draft/media-files",
        headers=headers,
        json=[{"key": "test.pdf"}],
    )


def upload_file(client, recid):
    """Create draft and return its id."""
    return client.put(
        f"/records/{recid}/draft/media-files/test.pdf/content",
        headers={
            "content-type": "application/octet-stream",
            "accept": "application/json",
        },
        data=BytesIO(b"testfile"),
    )


def commit_file(client, recid, headers):
    """Create draft and return its id."""
    return client.post(
        f"/records/{recid}/draft/media-files/test.pdf/commit", headers=headers
    )


def test_upload_media_files(
    client, headers, running_app, minimal_record, users, location, superuser
):
    login_user(client, users[0])

    recid = create_draft(client, minimal_record, headers)
    init_file(client, recid, headers)
    upload_file(client, recid)
    # upload file and commit
    response = commit_file(client, recid, headers)
    assert response.status_code == 200

    url = f"/records/{recid}/draft"

    response = client.get(url)
    assert response.json["media_files"]["enabled"]
    assert "test.pdf" in response.json["media_files"]["entries"].keys()
    assert response.json["media_files"]["count"] == 1

    logout_user(client)


def test_only_owners_can_delete_media_file(
    client, headers, running_app, minimal_record, users, location, superuser
):
    login_user(client, users[0])
    recid = create_draft(client, minimal_record, headers)
    init_file(client, recid, headers)
    upload_file(client, recid)
    # upload file and commit
    response = commit_file(client, recid, headers)
    logout_user(client)

    url = f"/records/{recid}/draft/media-files/test.pdf"

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


def test_only_owners_can_delete_all_files(
    client, headers, running_app, minimal_record, users, location, superuser
):
    login_user(client, users[0])
    recid = create_draft(client, minimal_record, headers)
    init_file(client, recid, headers)
    upload_file(client, recid)
    # upload file and commit
    response = commit_file(client, recid, headers)
    logout_user(client)

    url = f"/records/{recid}/draft/media-files"

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


def test_only_owners_can_list_draft_w_public_files(
    client, headers, running_app, minimal_record, users, location, superuser
):
    # drafts should only be seen by their owners (+ shared with soon)
    login_user(client, users[0])
    recid = create_draft(client, minimal_record, headers)
    init_file(client, recid, headers)
    upload_file(client, recid)
    # upload file and commit
    response = commit_file(client, recid, headers)
    logout_user(client)
    url = f"/records/{recid}/draft/media-files"

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


def test_list_media_files_for_deleted_record(
    client, headers, running_app, minimal_record, users, location, superuser
):
    login_user(client, users[0])

    recid = create_draft(client, minimal_record, headers)
    init_file(client, recid, headers)
    upload_file(client, recid)
    # upload file and commit
    response = commit_file(client, recid, headers)
    assert response.status_code == 200
    assert response.data
    publish_draft(client, recid, headers)
    logout_user(client)

    url = f"/records/{recid}/media-files"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/media-files/test.pdf"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/media-files/test.pdf/content"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/media-files-archive"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    login_user(client, superuser.user)

    # We delete the record
    delete_record(client, recid, headers)

    url = f"/records/{recid}/media-files"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/media-files/test.pdf?include_deleted=1"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/media-files/test.pdf/content"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/media-files-archive?include_deleted=1"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    logout_user(client)

    url = f"/records/{recid}/media-files"

    response = client.get(url, headers=headers)
    assert 410 == response.status_code
    assert response.data

    url = f"/records/{recid}/media-files/test.pdf"

    response = client.get(url, headers=headers)
    assert 410 == response.status_code
    assert response.data

    url = f"/records/{recid}/media-files/test.pdf/content"

    response = client.get(url, headers=headers)
    assert 410 == response.status_code
    assert response.data

    url = f"/records/{recid}/media-files-archive"

    response = client.get(url, headers=headers)
    assert 410 == response.status_code
    assert response.data
