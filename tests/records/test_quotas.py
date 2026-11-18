# SPDX-FileCopyrightText: 2025 TU Wien.
# SPDX-License-Identifier: MIT

import pytest
from invenio_access.permissions import system_identity
from invenio_db import db
from marshmallow import ValidationError

from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_rdm_records.proxies import current_rdm_records_storage_service
from invenio_rdm_records.records.models import RDMRecordQuota, RDMUserQuota


def test_user_quota(app, identity_simple, minimal_record, location, resource_type_v):
    """Test the effectiveness of ``RDMUserQuota`` for new drafts."""
    quota = (
        db.session.query(RDMUserQuota)
        .filter(RDMUserQuota.user_id == identity_simple.id)
        .one_or_none()
    )
    assert quota is None

    old_draft = records_service.create(identity_simple, minimal_record)._obj
    assert old_draft.bucket.quota_size == 1000000
    assert old_draft.bucket.max_file_size == 1000000

    # Set the user quota and see if new drafts are affected
    records_service.set_user_quota(
        system_identity, identity_simple.id, {"quota_size": 1337, "max_file_size": 420}
    )
    quota = (
        db.session.query(RDMUserQuota)
        .filter(RDMUserQuota.user_id == identity_simple.id)
        .one_or_none()
    )
    assert quota is not None
    assert quota.user_id == identity_simple.id
    assert quota.quota_size == 1337
    assert quota.max_file_size == 420

    draft = records_service.create(identity_simple, minimal_record)._obj
    assert draft.bucket.quota_size == 1337
    assert draft.bucket.max_file_size == 420

    # But old drafts shouldn't be affected
    draft = records_service.read_draft(identity_simple, old_draft.pid.pid_value)._obj
    assert draft.bucket.quota_size == 1000000
    assert draft.bucket.max_file_size == 1000000


def test_record_quota(app, identity_simple, minimal_record, location, resource_type_v):
    """Test the effectiveness of ``RDMRecordQuota``."""
    quota = (
        db.session.query(RDMRecordQuota)
        .filter(RDMRecordQuota.user_id == identity_simple.id)
        .one_or_none()
    )
    assert quota is None

    draft = records_service.create(identity_simple, minimal_record)._obj
    assert draft.bucket.quota_size == 1000000
    assert draft.bucket.max_file_size == 1000000

    # Set the record quota and see if it affected the existing draft
    records_service.set_quota(
        system_identity, draft.pid.pid_value, {"quota_size": 1337, "max_file_size": 420}
    )
    quota = (
        db.session.query(RDMRecordQuota)
        .filter(RDMRecordQuota.user_id == identity_simple.id)
        .one_or_none()
    )
    assert quota is not None
    assert quota.user_id == identity_simple.id
    assert quota.quota_size == 1337
    assert quota.max_file_size == 420

    draft = records_service.read_draft(identity_simple, draft.pid.pid_value)._obj
    assert draft.bucket.quota_size == 1337
    assert draft.bucket.max_file_size == 420

    # Check that a new version of the draft still has the same quota
    records_service.publish(identity_simple, draft.pid.pid_value)
    draft = records_service.new_version(identity_simple, draft.pid.pid_value)._obj
    assert draft.bucket.quota_size == 1337
    assert draft.bucket.max_file_size == 420


def _get_user_quota(user_id):
    return (
        db.session.query(RDMUserQuota)
        .filter(RDMUserQuota.user_id == user_id)
        .one_or_none()
    )


def test_user_max_additional_quota(app, identity_simple, monkeypatch):
    """Test the per-user override of the max additional quota."""
    monkeypatch.setitem(
        app.config, "RDM_FILES_DEFAULT_MAX_ADDITIONAL_QUOTA_SIZE", 50 * 10**9
    )
    storage_service = current_rdm_records_storage_service
    user_id = identity_simple.id

    # Without a user quota entry, the configured default is used
    assert storage_service.user_max_additional_quota(user_id) == 50 * 10**9
    assert storage_service.remaining_storage(user_id, None) == 50 * 10**9

    # Set a per-user value
    records_service.set_user_quota(
        system_identity,
        user_id,
        {
            "quota_size": 1337,
            "max_file_size": 420,
            "max_additional_quota_size": 200 * 10**9,
        },
    )
    assert _get_user_quota(user_id).max_additional_quota_size == 200 * 10**9
    assert storage_service.user_max_additional_quota(user_id) == 200 * 10**9
    assert storage_service.max_additional_quota_value(user_id) == 200 * 10**9
    assert storage_service.remaining_storage(user_id, None) == 200 * 10**9
    # The config default itself is unchanged
    assert storage_service.max_additional_quota == 50 * 10**9

    # Omitting the field leaves the stored value untouched
    records_service.set_user_quota(
        system_identity, user_id, {"quota_size": 2000, "max_file_size": 1000}
    )
    quota = _get_user_quota(user_id)
    assert quota.quota_size == 2000
    assert quota.max_additional_quota_size == 200 * 10**9

    # Zero is a valid override (no additional quota for this user)
    records_service.set_user_quota(
        system_identity,
        user_id,
        {"quota_size": 2000, "max_file_size": 1000, "max_additional_quota_size": 0},
    )
    assert storage_service.user_max_additional_quota(user_id) == 0
    assert storage_service.remaining_storage(user_id, None) == 0

    # Explicit null resets to the configured default
    records_service.set_user_quota(
        system_identity,
        user_id,
        {
            "quota_size": 2000,
            "max_file_size": 1000,
            "max_additional_quota_size": None,
        },
    )
    assert _get_user_quota(user_id).max_additional_quota_size is None
    assert storage_service.user_max_additional_quota(user_id) == 50 * 10**9

    # Negative values are rejected
    with pytest.raises(ValidationError):
        records_service.set_user_quota(
            system_identity,
            user_id,
            {
                "quota_size": 2000,
                "max_file_size": 1000,
                "max_additional_quota_size": -1,
            },
        )


def test_record_quota_rejects_max_additional_quota(
    app, identity_simple, minimal_record, location, resource_type_v
):
    """The per-user field is not accepted when setting a record's quota."""
    draft = records_service.create(identity_simple, minimal_record)._obj
    with pytest.raises(ValidationError):
        records_service.set_quota(
            system_identity,
            draft.pid.pid_value,
            {
                "quota_size": 1337,
                "max_file_size": 420,
                "max_additional_quota_size": 10,
            },
        )
