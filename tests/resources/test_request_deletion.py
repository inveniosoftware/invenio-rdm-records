# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test record request deletion resource."""

from datetime import date, timedelta

from flask import session
from invenio_db import db

from invenio_rdm_records.proxies import current_rdm_records_service as service


def test_success(uploader, client, record_factory, headers):
    """Test successful request deletion."""
    record = record_factory.create_record()

    uploader.login(client)
    resp = client.post(
        f"/records/{record.pid.pid_value}/request-deletion",
        json={"reason": "test-record"},
        headers=headers,
    )

    assert resp.status_code == 200
    assert resp.json["status"] == "accepted"
    request_id = resp.json["id"]
    assert f"/me/requests/{request_id}" in resp.json["links"]["self_html"]
    assert session["_flashes"] == [
        (
            "success",
            "Your record was deleted and from now on will resolve to this tombstone page.",
        )
    ]

    # Check the deleted record
    resp = client.get(f"/records/{record.pid.pid_value}")
    assert resp.status_code == 410
    assert resp.json["message"] == "Record deleted"
    assert resp.json["tombstone"]["removed_by"] == {"user": str(uploader.id)}
    assert resp.json["tombstone"]["is_visible"] is True
    assert resp.json["tombstone"]["removal_date"].startswith(date.today().isoformat())
    assert resp.json["tombstone"]["removal_reason"] == {"id": "test-record"}
    assert resp.json["tombstone"]["deletion_policy"] == {"id": "grace-period-v1"}


def test_request_flow(uploader, superuser, client, record_factory, headers):
    """Test request deletion flow."""
    record = record_factory.create_record()

    # Set the record creation date beyond the 30-day immediate deletion grace period
    record.model.created -= timedelta(days=31)
    db.session.commit()

    uploader.login(client)
    resp = client.post(
        f"/records/{record.pid.pid_value}/request-deletion",
        json={"reason": "test-record", "comment": "Test request deletion comment"},
        headers=headers,
    )

    assert resp.status_code == 201
    assert resp.json["status"] == "submitted"
    # No flashed messages, since there was no immediate deletion
    assert "_flashes" not in session
    request_id = resp.json["id"]

    # Accept the request as superuser
    superuser.login(client, logout_first=True)
    resp = client.post(f"/requests/{request_id}/actions/accept", headers=headers)
    assert resp.status_code == 200
    assert resp.json["status"] == "accepted"

    # Check the deleted record
    uploader.login(client, logout_first=True)
    resp = client.get(f"/records/{record.pid.pid_value}")
    assert resp.status_code == 410
    assert resp.json["message"] == "Record deleted"
    assert resp.json["tombstone"]["removed_by"] == {"user": str(superuser.id)}
    assert resp.json["tombstone"]["is_visible"] is True
    assert resp.json["tombstone"]["note"] == ""
    assert resp.json["tombstone"]["removal_date"].startswith(date.today().isoformat())
    assert resp.json["tombstone"]["removal_reason"] == {"id": "test-record"}
    assert "deletion_policy" not in resp.json["tombstone"]


def test_feature_disabled(
    uploader, client, set_app_config_fn_scoped, record_factory, headers
):
    """Test endpoint returns 403 when deletion features are disabled."""
    uploader.login(client)
    record = record_factory.create_record()

    set_app_config_fn_scoped(
        {
            "RDM_IMMEDIATE_RECORD_DELETION_ENABLED": False,
            "RDM_REQUEST_RECORD_DELETION_ENABLED": False,
        }
    )

    resp = client.post(
        f"/records/{record.pid.pid_value}/request-deletion",
        json={"reason": "test-record"},
        headers=headers,
    )
    assert resp.status_code == 403


def test_invalid_record(client_with_login, headers):
    """Test endpoint returns 404 for non-existent record."""
    client = client_with_login
    resp = client.post(
        "/records/non-existent-id/request-deletion",
        json={"reason": "test-record"},
        headers=headers,
    )

    assert resp.status_code == 404


def test_already_deleted(uploader, superuser, client, record_factory, headers):
    """Test endpoint returns appropriate error for already deleted record."""
    record = record_factory.create_record()

    # Delete the record first using service (administrative deletion by superuser)
    service.delete_record(superuser.identity, record.pid.pid_value, {})

    uploader.login(client)
    resp = client.post(
        f"/records/{record.pid.pid_value}/request-deletion",
        json={"reason": "test-record"},
        headers=headers,
    )

    assert resp.status_code == 400
    assert resp.json["message"] == "Record in unexpected deletion status."
