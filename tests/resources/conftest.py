# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

from io import BytesIO

import pytest
from invenio_app.factory import create_api


@pytest.fixture(scope="module")
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


def link(url):
    """Strip the host part of a link."""
    api_prefix = "https://127.0.0.1:5000/api"
    if url.startswith(api_prefix):
        return url[len(api_prefix) :]


@pytest.fixture(scope="function")
def app_with_allowed_edits(running_app):
    """Allow editing of published records."""
    running_app.app.config["RDM_LOCK_EDIT_PUBLISHED_FILES"] = lambda *_, **__: False
    return running_app


@pytest.fixture(scope="function")
def app_with_deny_edits(running_app):
    """Deny editing of published records."""
    running_app.app.config["RDM_LOCK_EDIT_PUBLISHED_FILES"] = lambda *_, **__: True


def init_file(client, recid, key, headers):
    """Init a file for draft with given recid."""
    return client.post(
        f"/records/{recid}/draft/files",
        headers=headers,
        json=[{"key": key}],
    )


def upload_file(client, recid, key):
    """Create draft and return its id."""
    return client.put(
        f"/records/{recid}/draft/files/{key}/content",
        headers={
            "content-type": "application/octet-stream",
            "accept": "application/json",
        },
        data=BytesIO(b"testfile"),
    )


def commit_file(client, recid, key, headers):
    """Create draft and return its id."""
    return client.post(f"/records/{recid}/draft/files/{key}/commit", headers=headers)


@pytest.fixture()
def publish_record(headers):
    """Factory fixture that publishes a record."""

    def _publish_record(client, json):
        draft = client.post("/records", headers=headers, json=json)
        assert 201 == draft.status_code
        record = client.post(link(draft.json["links"]["publish"]), headers=headers)
        assert 202 == record.status_code
        record = client.get(link(record.json["links"]["self"]), headers=headers)
        assert 200 == record.status_code
        return record.json

    return _publish_record
