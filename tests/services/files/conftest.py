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


def init_file(client, recid, key, headers):
    """Init a file for draft with given recid."""
    return client.post(
        f"/records/{recid}/draft/files",
        headers=headers,
        json=[{"key": key}],
    )


@pytest.fixture(scope="function")
def db(database):
    """Overrides the `pytest_invenio.db` to force db recreation.

    Scope: function

    Force the recreation of the database as nested sessions are misbehaving with
    sqlalchemy-continuum.
    """
    yield database


@pytest.fixture(scope="function")
def app_with_allowed_edits(running_app):
    """This app allows the edit of files after publish.

    Note: this fixture utilizes an overriden `db` fixture that doesn't use nested
    sessions as we want to test sqlalchemy-continuum and the latter misbehaves when the
    default `pytest_invenio.db` fixture is used. Thus,
    """
    running_app.app.config["RDM_LOCK_EDIT_PUBLISHED_FILES"] = lambda *_, **__: False
    return running_app


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
