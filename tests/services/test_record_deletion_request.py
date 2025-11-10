# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test deletion service integration."""

from datetime import date, timedelta

import pytest
from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.services.errors import PermissionDeniedError
from marshmallow import ValidationError

from invenio_rdm_records.proxies import current_rdm_records_service as service
from invenio_rdm_records.records.systemfields.deletion_status import (
    RecordDeletionStatusEnum,
)
from invenio_rdm_records.services.errors import (
    DeletionStatusException,
    RecordDeletedException,
)


def test_request_deletion_feature_disabled(
    record_factory, search_clear, set_app_config_fn_scoped, uploader, test_user
):
    """Test request_deletion when both features are disabled."""
    record = record_factory.create_record()

    set_app_config_fn_scoped(
        {
            "RDM_IMMEDIATE_RECORD_DELETION_ENABLED": False,
            "RDM_REQUEST_RECORD_DELETION_ENABLED": False,
        }
    )

    # Any user should get permission denied when features are disabled
    with pytest.raises(PermissionDeniedError):
        service.request_deletion(uploader.identity, record["id"], {})
    with pytest.raises(PermissionDeniedError):
        service.request_deletion(test_user.identity, record["id"], {})


def test_request_deletion_immediate_allowed(record_factory, search_clear, uploader):
    """Test immediate deletion when grace period policy allows it."""
    record = record_factory.create_record()

    # Should immediately delete the record (accepted request), since the record is
    # within the 30-day grace period
    request = service.request_deletion(
        uploader.identity,
        record["id"],
        {"reason": "test-record"},
    ).data
    assert request["status"] == "accepted"

    # Verify record is deleted
    deleted_record = service.record_cls.pid.resolve(record["id"])
    assert deleted_record.deletion_status == RecordDeletionStatusEnum.DELETED
    assert deleted_record.tombstone.removal_reason["id"] == "test-record"
    assert deleted_record.tombstone.removed_by["user"] == str(uploader.id)
    assert deleted_record.tombstone.removal_date.startswith(date.today().isoformat())
    assert deleted_record.tombstone.is_visible is True
    assert deleted_record.tombstone.deletion_policy["id"] == "grace-period-v1"


def test_request_deletion_request_only(record_factory, search_clear, uploader):
    """Test request deletion when only request policy applies."""
    record = record_factory.create_record()

    # Set the creation date to 31 days ago to force the request flow
    record.model.created -= timedelta(days=31)
    db.session.commit()

    # Should create a submitted request (not immediately accepted)
    request = service.request_deletion(
        uploader.identity,
        record["id"],
        data={"reason": "test-record", "comment": "Test request deletion comment"},
    ).data

    assert request["status"] == "submitted"
    assert request["payload"] == {
        "reason": "test-record",
        "comment": "Test request deletion comment",
    }
    assert request["created_by"] == {"user": str(uploader.id)}
    assert request["receiver"] is None
    assert request["topic"] == {"record": str(record["id"])}

    # Verify record is NOT deleted yet
    not_deleted_record = service.record_cls.pid.resolve(record["id"])
    assert not_deleted_record.deletion_status == RecordDeletionStatusEnum.PUBLISHED
    assert not_deleted_record.tombstone is None


def test_request_deletion_duplicate_prevention(record_factory, search_clear, uploader):
    """Test that duplicate deletion requests are prevented."""
    record = record_factory.create_record()

    # Set the creation date to 31 days ago to force the request flow
    record.model.created -= timedelta(days=31)
    db.session.commit()

    data = {"reason": "test-record", "comment": "First request"}

    # Create first request
    request = service.request_deletion(uploader.identity, record["id"], data).data
    assert request["status"] == "submitted"

    # Try to create second request - should fail
    with pytest.raises(ValidationError) as exc:
        service.request_deletion(uploader.identity, record["id"], data)
    assert exc.value.normalized_messages() == {
        "_schema": "A deletion request for this record already exists."
    }


def test_request_deletion_invalid_reason(record_factory, search_clear, uploader):
    """Test that invalid removal reasons are rejected."""
    record = record_factory.create_record()

    # The "spam" removal reason doesn't have the "deletion-request" tag
    data = {"reason": "spam", "comment": "Test invalid reason"}

    # Immediate deletion should fail
    with pytest.raises(ValidationError) as exc:
        service.request_deletion(uploader.identity, record["id"], data)
    assert exc.value.normalized_messages() == {"_schema": "Invalid removal reason"}

    # Set the creation date to 31 days ago to force the request flow
    record.model.created -= timedelta(days=31)
    db.session.commit()

    # Deletion request should fail
    with pytest.raises(ValidationError) as exc:
        service.request_deletion(uploader.identity, record["id"], data)
    assert exc.value.normalized_messages() == {"_schema": "Invalid removal reason"}


def test_request_deletion_already_deleted_record(
    superuser_identity, record_factory, search_clear, uploader
):
    """Test request_deletion with already deleted record."""
    record = record_factory.create_record()

    # Delete the record first using superuser for administrative deletion
    service.delete_record(superuser_identity, record["id"], {})

    # Try to request deletion as original owner (should fail - already deleted)
    with pytest.raises(DeletionStatusException):
        service.request_deletion(uploader.identity, record["id"])


def test_request_deletion_invalid_record(running_app, test_user):
    """Test request_deletion with non-existent record."""
    user_identity = test_user.identity
    with pytest.raises(PIDDoesNotExistError):
        service.request_deletion(user_identity, "non-existent-id")


def test_tombstone_deletion_policy_field_manual_deletion(
    superuser_identity, record_factory, search_clear
):
    """Test that deletion_policy field is None for manual deletion (not via request_deletion)."""
    record = record_factory.create_record()

    # Delete manually using superuser for administrative deletion (not via request_deletion)
    service.delete_record(
        superuser_identity,
        record["id"],
        {"note": "Manual deletion"},
    )

    # Check tombstone has no deletion_policy field
    deleted_record = service.record_cls.pid.resolve(record["id"])
    tombstone = deleted_record.tombstone

    assert tombstone.deletion_policy is None


def test_tombstone_deletion_policy_serialization(
    record_factory, search_clear, uploader
):
    """Test that deletion_policy field serializes correctly."""
    record = record_factory.create_record()

    service.request_deletion(
        uploader.identity,
        record["id"],
        data={"reason": "test-record"},
    )

    # Read the record via service to get serialized version
    with pytest.raises(RecordDeletedException) as exc:
        service.read(uploader.identity, record["id"])
    deleted_record = exc.value.result_item.data

    assert deleted_record["tombstone"]["removal_reason"]["id"] == "test-record"
    assert deleted_record["tombstone"]["removed_by"] == {"user": str(uploader.id)}
    assert deleted_record["tombstone"]["removal_date"] == date.today().isoformat()
    assert deleted_record["tombstone"]["is_visible"] is True
    assert deleted_record["tombstone"]["deletion_policy"] == {"id": "grace-period-v1"}
