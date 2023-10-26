# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test some permissions on RDMRecordFilesResource.

Not every case is tested, but enough high-level ones for it to be useful.
"""

from tests.helpers import login_user, logout_user
from tests.resources.conftest import commit_file, init_file, link, upload_file


def create_draft(client, record, headers):
    """Create draft ready for file attachment and return its id."""
    record["files"] = {"enabled": True}
    response = client.post("/records", json=record, headers=headers)
    assert response.status_code == 201
    return response.json


def delete_record(client, recid, headers):
    """Soft delete a record."""
    response = client.delete(f"/records/{recid}/delete", json={}, headers=headers)
    assert response.status_code == 204
    response.close()


def attach_file(client, recid, key, headers):
    """Attach a file to a record."""

    init_file(client, recid, key, headers)
    upload_file(client, recid, key)
    # upload file and commit
    commit_file(client, recid, key, headers)


def test_published_record_files_allow_edit(
    client, headers, app_with_allowed_edits, minimal_record, users, location, superuser
):
    login_user(client, users[0])

    draft = create_draft(client, minimal_record, headers)
    recid = draft["id"]

    # attach 1 file
    attach_file(client, recid, "test.pdf", headers)

    draft = client.get(link(draft["links"]["self"])).json
    assert draft["files"]["enabled"]
    assert "test.pdf" in draft["files"]["entries"].keys()
    assert draft["files"]["count"] == 1

    # publish the draft
    published_record = client.post(
        link(draft["links"]["publish"]), headers=headers
    ).json

    # edit published draft to modify files
    draft = client.post(link(published_record["links"]["draft"])).json

    # attach a 2nd file
    attach_file(client, draft["id"], "test2.pdf", headers)

    # delete the 1st file
    url = f"{draft['links']['files']}/test.pdf"
    response = client.delete(link(url), headers=headers)
    assert response.status_code == 204

    # publish the draft again
    published_record = client.post(
        link(draft["links"]["publish"]), headers=headers
    ).json

    assert published_record["files"]["enabled"]
    assert "test2.pdf" in published_record["files"]["entries"].keys()
    assert published_record["files"]["count"] == 1

    logout_user(client)


def test_published_record_files_deny_edit(
    client, headers, app_with_deny_edits, minimal_record, users, location, superuser
):
    login_user(client, users[0])

    draft = create_draft(client, minimal_record, headers)
    recid = draft["id"]

    # attach file
    attach_file(client, recid, "test.pdf", headers)

    draft = client.get(link(draft["links"]["self"])).json
    assert draft["files"]["enabled"]
    assert "test.pdf" in draft["files"]["entries"].keys()
    assert draft["files"]["count"] == 1

    # publish the draft
    published_record = client.post(
        link(draft["links"]["publish"]), headers=headers
    ).json

    # edit published draft to modify files
    draft = client.post(link(published_record["links"]["draft"])).json

    # Owner can't add file
    login_user(client, users[0])
    # attach_file(client, recid, "test3.pdf", headers, expected_status=403)
    init_file(client, recid, "test3.pdf", headers)
    response = upload_file(client, recid, "test3.pdf")
    # the upload of a file is the one that is affected when we lock the bucket
    assert response.status_code == 403
    logout_user(client)


def test_files_api_flow_for_deleted_record(
    client, headers, running_app, minimal_record, users, location, superuser
):
    login_user(client, users[0])

    draft = create_draft(client, minimal_record, headers)
    recid = draft["id"]

    attach_file(client, recid, "test.pdf", headers)

    # publish the draft
    response = client.post(link(draft["links"]["publish"]), headers=headers)
    assert response.status_code == 202
    assert response.data

    logout_user(client)

    url = f"/records/{recid}/files"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/files/test.pdf"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/files/test.pdf/content"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/files-archive"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    login_user(client, superuser.user)

    # We delete the record
    delete_record(client, recid, headers)

    # Superuser has access to record
    url = f"/records/{recid}/files"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/files/test.pdf"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/files/test.pdf/content"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/files-archive"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    logout_user(client)

    # Non superuser users have no access to the record
    url = f"/records/{recid}/files"

    response = client.get(url, headers=headers)
    assert 410 == response.status_code
    assert response.data

    url = f"/records/{recid}/files/test.pdf"

    response = client.get(url, headers=headers)
    assert 410 == response.status_code
    assert response.data

    url = f"/records/{recid}/files/test.pdf/content"

    response = client.get(url, headers=headers)
    assert 410 == response.status_code
    assert response.data

    url = f"/records/{recid}/files-archive"

    response = client.get(url, headers=headers)
    assert 410 == response.status_code
    assert response.data


def test_filename_with_slash_flow_for_deleted_record_(
    client, headers, running_app, minimal_record, users, location, superuser
):
    login_user(client, users[0])

    draft = create_draft(client, minimal_record, headers)
    recid = draft["id"]
    filename = "folder/test.pdf"

    attach_file(client, recid, filename, headers)

    # publish the draft
    response = client.post(link(draft["links"]["publish"]), headers=headers)
    assert response.status_code == 202
    assert response.data

    logout_user(client)

    url = f"/records/{recid}/files"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/files/{filename}"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/files/{filename}/content"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/files-archive"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    login_user(client, superuser.user)

    # We delete the record
    delete_record(client, recid, headers)

    # Superuser has access to record
    url = f"/records/{recid}/files"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/files/{filename}"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/files/{filename}/content"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    url = f"/records/{recid}/files-archive"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    logout_user(client)

    # Non superuser users have no access to the record
    url = f"/records/{recid}/files"

    response = client.get(url, headers=headers)
    assert 410 == response.status_code
    assert response.data

    url = f"/records/{recid}/files/{filename}"

    response = client.get(url, headers=headers)
    assert 410 == response.status_code
    assert response.data

    url = f"/records/{recid}/files/{filename}/content"

    response = client.get(url, headers=headers)
    assert 410 == response.status_code
    assert response.data

    url = f"/records/{recid}/files-archive"

    response = client.get(url, headers=headers)
    assert 410 == response.status_code
    assert response.data


def test_upload_and_access_filename_with_slash(
    client, headers, app_with_deny_edits, minimal_record, users, location, superuser
):
    login_user(client, users[0])

    draft = create_draft(client, minimal_record, headers)
    recid = draft["id"]

    # Define a file name with a slash in it
    file_name = "folder/test.pdf"

    # Attach the file with the slash in its name
    attach_file(client, draft["id"], file_name, headers)

    draft = client.get(link(draft["links"]["self"])).json
    assert draft["files"]["enabled"]
    assert file_name in draft["files"]["entries"].keys()
    assert draft["files"]["count"] == 1

    # Publish the draft
    published_record = client.post(
        link(draft["links"]["publish"]), headers=headers
    ).json

    # Access the uploaded file
    url = f"/records/{recid}/files/{file_name}"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    # Access the content of the uploaded file
    url = f"/records/{recid}/files/{file_name}/content"

    response = client.get(url, headers=headers)
    assert 200 == response.status_code
    assert response.data

    logout_user(client)
