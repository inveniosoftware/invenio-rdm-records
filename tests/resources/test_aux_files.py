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

import pytest

from tests.helpers import login_user, logout_user


def create_draft(client, record, headers):
    """Create draft ready for file attachment and return its id."""
    record["media_files"] = {"enabled": True}
    response = client.post("/records", json=record, headers=headers)
    assert response.status_code == 201
    return response.json["id"]


def init_file(client, recid, headers):
    """Init a file for draft with given recid."""
    return client.post(
        f"/records/{recid}/draft/media-files", headers=headers, json=[{"key": "test.pdf"}]
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
    return client.post(f"/records/{recid}/draft/media-files/test.pdf/commit", headers=headers)


def test_upload_media_files(
    client,
    headers,
    minimal_record,
    users,
    superuser,
    metadata_only_records_disabled,
):
    login_user(client, users[0])

    recid = create_draft(client, minimal_record, headers)
    init_file(client, recid, headers)
    upload_file(client, recid)
    # upload file and commit
    response = commit_file(client, recid, headers)
    assert response.status_code == 200

    assert response.json["id"] == recid
    url = f"/records/{recid}/draft"


    response = client.get(url)
    assert response.json["media_files"]["enabled"]
    assert "test.pdf" in response.json["media_files"]["entries"].keys()
    assert response.json["media_files"]["count"] == 1

    # Admin
    logout_user(client)
    login_user(client, superuser.user)
