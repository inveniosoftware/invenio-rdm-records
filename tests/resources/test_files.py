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
