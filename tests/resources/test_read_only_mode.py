# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

import json
from datetime import datetime, timedelta, timezone
from io import BytesIO

import arrow
import pytest
from invenio_requests import current_requests_service

from invenio_rdm_records.records import RDMDraft, RDMRecord
from invenio_rdm_records.requests import CommunitySubmission


@pytest.fixture()
def rw_app(running_app):
    running_app.app.config["RECORDS_PERMISSIONS_READ_ONLY"] = False
    yield running_app.app
    running_app.app.config["RECORDS_PERMISSIONS_READ_ONLY"] = False


def test_create_draft_ro(
    rw_app, client_with_login, minimal_record, headers, search_clear
):
    client = client_with_login
    rw_app.config["RECORDS_PERMISSIONS_READ_ONLY"] = True
    response = client.post("/records", headers=headers, data=minimal_record)

    assert response.status_code == 403


def test_create_draft_ro(
    rw_app, client_with_login, minimal_record, headers, search_clear
):
    client = client_with_login
    rw_app.config["RECORDS_PERMISSIONS_READ_ONLY"] = True
    response = client.post("/records", headers=headers, data=minimal_record)

    assert response.status_code == 403
