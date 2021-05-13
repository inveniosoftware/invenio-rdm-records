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


from io import BytesIO

import flask_security
import pytest
from invenio_accounts.testutils import login_user_via_session


def login_user(client, user):
    """Log user in."""
    flask_security.login_user(user, remember=True)
    login_user_via_session(client, email=user.email)


def logout_user(client):
    """Log current user out."""
    flask_security.logout_user()
    with client.session_transaction() as session:
        session.pop("user_id", None)


def create_record_w_file(client, record, headers):
    """Create record with a file."""
    # Create draft
    record["files"] = {"enabled": True}
    response = client.post("/records", json=record, headers=headers)
    assert response.status_code == 201
    recid = response.json['id']

    # Attach a file to it
    response = client.post(
        f'/records/{recid}/draft/files',
        headers=headers,
        json=[{'key': 'test.pdf'}]
    )
    assert response.status_code == 201
    response = client.put(
        f"/records/{recid}/draft/files/test.pdf/content",
        headers={
            'content-type': 'application/octet-stream',
            'accept': 'application/json',
        },
        data=BytesIO(b'testfile'),
    )
    assert response.status_code == 200
    response = client.post(
        f"/records/{recid}/draft/files/test.pdf/commit",
        headers=headers
    )
    assert response.status_code == 200

    # Publish it
    response = client.post(
        f"/records/{recid}/draft/actions/publish", headers=headers
    )
    assert response.status_code == 202

    return recid


@pytest.fixture(scope='function')
def record_w_restricted_file(
        client, headers, running_app, minimal_record, users):
    # Login
    login_user(client, users[0])

    # NOTE: This covers all scenarios of file restriction.
    #       (e.g. restricted record has its files restricted too)
    restricted_files_record = minimal_record
    restricted_files_record["access"]["files"] = "restricted"

    recid = create_record_w_file(client, restricted_files_record, headers)

    # Logout
    logout_user(client)

    return recid


def test_only_owners_can_list_restricted_files(
        client, headers, record_w_restricted_file, users):
    recid = record_w_restricted_file
    url = f"/records/{recid}/files"

    # Anonymous user can't list files
    response = client.get(url, headers=headers)
    assert response.status_code == 403

    # Different user can't list files
    login_user(client, users[1])
    response = client.get(url, headers=headers)
    assert response.status_code == 403
    logout_user(client)

    # Owner can list files
    login_user(client, users[0])
    response = client.get(url, headers=headers)
    assert response.status_code == 200


def test_only_owners_can_read_restricted_file_metadata(
        client, headers, record_w_restricted_file, users):
    recid = record_w_restricted_file
    url = f"/records/{recid}/files/test.pdf"

    # Anonymous user can't read file metadata
    response = client.get(url, headers=headers)
    assert response.status_code == 403

    # Different user can't read file metadata
    login_user(client, users[1])
    response = client.get(url, headers=headers)
    assert response.status_code == 403
    logout_user(client)

    # Owner can read file metadata
    login_user(client, users[0])
    response = client.get(url, headers=headers)
    assert response.status_code == 200


def test_only_owners_can_download_restricted_file(
        client, headers, record_w_restricted_file, users):
    recid = record_w_restricted_file
    url = f"/records/{recid}/files/test.pdf/content"

    # Anonymous user can't download file
    response = client.get(url, headers=headers)
    assert response.status_code == 403

    # Different user can't download file
    login_user(client, users[1])
    response = client.get(url, headers=headers)
    assert response.status_code == 403
    logout_user(client)

    # Owner can download file
    login_user(client, users[0])
    response = client.get(url, headers=headers)
    assert response.status_code == 200


def test_record_files_cannot_be_deleted(
        client, headers, record_w_restricted_file, users):
    recid = record_w_restricted_file
    url = f"/records/{recid}/files/test.pdf"

    # Anonymous user can't delete a file
    response = client.delete(url, headers=headers)
    assert response.status_code == 405

    # Different user can't delete file
    login_user(client, users[1])
    response = client.delete(url, headers=headers)
    assert response.status_code == 405
    logout_user(client)

    # Owner can't delete a file
    login_user(client, users[0])
    response = client.delete(url, headers=headers)
    assert response.status_code == 405


def test_files_cannot_be_uploaded_to_records(
        client, headers, record_w_restricted_file, users):
    recid = record_w_restricted_file
    url = f"/records/{recid}/files"

    # Anonymous user can't upload a file
    response = client.post(url, headers=headers, json=[{'key': 'test.pdf'}])
    assert response.status_code == 405

    # Different user can't upload a file
    login_user(client, users[1])
    response = client.post(url, headers=headers, json=[{'key': 'test.pdf'}])
    assert response.status_code == 405
    logout_user(client)

    # Owner can't upload a file
    login_user(client, users[0])
    response = client.post(url, headers=headers, json=[{'key': 'test.pdf'}])
    assert response.status_code == 405


def test_record_files_options_cannot_be_modified(
        client, headers, record_w_restricted_file, users):
    recid = record_w_restricted_file
    url = f"/records/{recid}/files"

    # Anonymous user can't modify record file options
    response = client.put(
        url, headers=headers, json=[{'default_preview': 'test.pdf'}]
    )
    assert response.status_code == 405

    # Different user can't modify record file options
    login_user(client, users[1])
    response = client.put(
        url, headers=headers, json=[{'default_preview': 'test.pdf'}]
    )
    assert response.status_code == 405
    logout_user(client)

    # Owner can't modify record file options
    login_user(client, users[0])
    response = client.put(
        url, headers=headers, json=[{'default_preview': 'test.pdf'}]
    )
    assert response.status_code == 405


def test_record_files_cannot_be_imported(
        client, headers, record_w_restricted_file, users):
    recid = record_w_restricted_file
    url = f"/records/{recid}/actions/files-import"

    # Anonymous user can't import record files
    response = client.post(url, headers=headers)
    assert response.status_code == 404

    # Different user can't modify record file options
    login_user(client, users[1])
    response = response = client.post(url, headers=headers)
    assert response.status_code == 404
    logout_user(client)

    # Owner can't modify record file options
    login_user(client, users[0])
    response = response = client.post(url, headers=headers)
    assert response.status_code == 404
