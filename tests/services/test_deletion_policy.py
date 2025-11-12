# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test deletion policy classes."""

from datetime import timedelta

from invenio_db import db

from invenio_rdm_records.services.request_policies import (
    GracePeriodPolicy,
    RDMRecordDeletionPolicy,
)


def test_grace_period_policy(record_factory, uploader, test_user):
    """Test grace period policy permission check and evaluation logic."""
    policy = GracePeriodPolicy(grace_period=timedelta(days=30))
    record = record_factory.create_record()

    owner_identity = uploader.identity
    non_owner_identity = test_user.identity

    # Test owner is allowed
    assert policy.is_allowed(owner_identity, record) is True
    # Test non-owner is not allowed
    assert policy.is_allowed(non_owner_identity, record) is False
    # Test within grace period (record just created, so well within 30 days)
    assert policy.evaluate(owner_identity, record) is True

    # Test outside grace period by setting the record creation date in the past
    record.model.created -= timedelta(days=31)
    db.session.commit()

    # Test owner is allowed
    assert policy.is_allowed(owner_identity, record) is True
    # Test non-owner is still not allowed
    assert policy.is_allowed(non_owner_identity, record) is False
    # But the policy evaluates to False
    assert policy.evaluate(owner_identity, record) is False


def test_deletion_policy_evaluation_feature_flags(
    record_factory, uploader, set_app_config_fn_scoped
):
    """Test policy evaluation when features are disabled."""
    record = record_factory.create_record()
    owner_identity = uploader.identity

    result = RDMRecordDeletionPolicy.evaluate(owner_identity, record)
    assert result["immediate_deletion"].enabled is True
    assert result["request_deletion"].enabled is True

    # Disable the deletion request features
    set_app_config_fn_scoped(
        {
            "RDM_IMMEDIATE_RECORD_DELETION_ENABLED": False,
            "RDM_REQUEST_RECORD_DELETION_ENABLED": False,
        }
    )

    result = RDMRecordDeletionPolicy.evaluate(owner_identity, record)
    assert result["immediate_deletion"].enabled is False
    assert result["request_deletion"].enabled is False


def test_deletion_policy_immediate_deletion(record_factory, uploader):
    """Test policy evaluation with policies configured."""
    record = record_factory.create_record()
    owner_identity = uploader.identity

    # Record just created, so within grace period (default 30 days)
    result = RDMRecordDeletionPolicy.evaluate(owner_identity, record)

    assert result["immediate_deletion"].enabled is True
    assert result["immediate_deletion"].allowed is True
    assert result["immediate_deletion"].policy["id"] == "grace-period-v1"

    assert result["request_deletion"].enabled is True
    assert result["request_deletion"].allowed is True
    assert result["request_deletion"].policy["id"] == "request-deletion-v1"


def test_deletion_policy_fallback_to_request(record_factory, uploader):
    """Test fallback to request deletion when grace period expires."""
    record = record_factory.create_record()
    owner_identity = uploader.identity

    # Set time to 31 days after record creation (outside 30-day grace period)
    record.model.created -= timedelta(days=31)
    db.session.commit()

    result = RDMRecordDeletionPolicy.evaluate(owner_identity, record)

    assert result["immediate_deletion"].enabled is True
    assert result["immediate_deletion"].allowed is False

    assert result["request_deletion"].enabled is True
    assert result["request_deletion"].allowed is True
    assert result["request_deletion"].policy["id"] == "request-deletion-v1"


def test_deletion_policy_non_owner(minimal_record, record_factory, test_user):
    """Test policy evaluation for non-owner users."""
    record = record_factory.create_record(minimal_record)
    non_owner_identity = test_user.identity

    result = RDMRecordDeletionPolicy.evaluate(non_owner_identity, record)

    # Non-owners should not be allowed to delete
    assert result["immediate_deletion"].valid_user is False
    assert result["immediate_deletion"].allowed is False

    assert result["request_deletion"].valid_user is False
    assert result["request_deletion"].allowed is False
