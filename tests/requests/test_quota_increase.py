# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Test quota increase requests."""

import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.services.errors import PermissionDeniedError
from sqlalchemy import event

from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_rdm_records.records.models import RDMRecordQuota
from invenio_rdm_records.services.request_policies import QuotaIncreasePolicy

GB = 10**9


def _quota(size_gb):
    return {"quota_size": size_gb * GB, "max_file_size": size_gb * GB}


@pytest.fixture(scope="module")
def app_config(app_config):
    """Enable self-service quota increases."""
    app_config["RDM_IMMEDIATE_QUOTA_INCREASE_ENABLED"] = True
    app_config["RDM_IMMEDIATE_QUOTA_INCREASE_POLICIES"] = [QuotaIncreasePolicy()]
    app_config["RDM_FILES_DEFAULT_QUOTA_SIZE"] = 10 * 10**9
    app_config["RDM_FILES_DEFAULT_MAX_ADDITIONAL_QUOTA_SIZE"] = 50 * 10**9
    return app_config


def test_quota_increase_with_non_integer_pid(
    running_app, minimal_record, uploader, location
):
    """Quota increase works with the default (non-integer) record identifiers."""
    draft = records_service.create(uploader.identity, minimal_record)
    assert not draft.id.isdigit()  # the default provider mints alphanumeric ids

    records_service.quota_increase(uploader.identity, draft.id, {"quota_size": "20"})

    draft = records_service.read_draft(uploader.identity, draft.id)
    assert draft._record.files.bucket.quota_size == 20 * 10**9


def test_quota_increase_per_user_cap(running_app, minimal_record, uploader, location):
    """Grants across drafts cannot exceed the per-user cap."""
    drafts = [
        records_service.create(uploader.identity, minimal_record) for _ in range(6)
    ]

    for draft in drafts[:5]:
        records_service.quota_increase(
            uploader.identity, draft.id, {"quota_size": "20"}
        )

    with pytest.raises(PermissionDeniedError):
        records_service.quota_increase(
            uploader.identity, drafts[5].id, {"quota_size": "20"}
        )

    rows = RDMRecordQuota.query.filter(
        RDMRecordQuota.user_id == uploader.identity.id
    ).all()
    assert len(rows) == 5
    total = sum(r.quota_size for r in rows)
    assert total == 5 * 20 * 10**9


def test_quota_increase_same_draft_update(
    running_app, minimal_record, uploader, location
):
    """Updating the same draft does not double count."""
    draft = records_service.create(uploader.identity, minimal_record)
    records_service.quota_increase(uploader.identity, draft.id, {"quota_size": "20"})
    records_service.quota_increase(uploader.identity, draft.id, {"quota_size": "30"})

    draft = records_service.read_draft(uploader.identity, draft.id)
    assert draft._record.files.bucket.quota_size == 30 * 10**9


def test_quota_increase_single_record_max(
    running_app, minimal_record, uploader, location
):
    """Single record cannot exceed 10GB default + 50GB."""
    draft = records_service.create(uploader.identity, minimal_record)

    with pytest.raises(PermissionDeniedError):
        records_service.quota_increase(
            uploader.identity, draft.id, {"quota_size": "100"}
        )


def test_quota_increase_locks_user_before_policy_check(
    running_app, minimal_record, uploader, location, db
):
    """The user's row is locked before the granted quotas are read."""
    if db.engine.dialect.name != "postgresql":
        pytest.skip("Row locks are only emitted on PostgreSQL.")
    draft = records_service.create(uploader.identity, minimal_record)

    statements = []

    def _record(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(db.engine, "before_cursor_execute", _record)
    try:
        records_service.quota_increase(
            uploader.identity, draft.id, {"quota_size": "20"}
        )
    finally:
        event.remove(db.engine, "before_cursor_execute", _record)

    lock_idx = next(
        i
        for i, s in enumerate(statements)
        if "accounts_user" in s and "FOR NO KEY UPDATE" in s
    )
    quota_sum_idx = next(
        i for i, s in enumerate(statements) if "rdm_records_quota" in s and "sum(" in s
    )
    assert lock_idx < quota_sum_idx


def test_admin_set_quota_not_capped(running_app, minimal_record, uploader, location):
    """Admin quota changes are not limited by the per-user cap."""
    draft = records_service.create(uploader.identity, minimal_record)
    records_service.set_quota(system_identity, draft.id, _quota(100))

    draft = records_service.read_draft(uploader.identity, draft.id)
    assert draft._record.files.bucket.quota_size == 100 * GB


def test_quota_below_default_does_not_add_allowance(
    running_app, minimal_record, uploader, location
):
    """A record with a quota below the default does not free up extra quota."""
    drafts = [
        records_service.create(uploader.identity, minimal_record) for _ in range(2)
    ]
    records_service.set_quota(system_identity, drafts[0].id, _quota(1))

    with pytest.raises(PermissionDeniedError):
        records_service.quota_increase(
            uploader.identity, drafts[1].id, {"quota_size": "61"}
        )

    records_service.quota_increase(
        uploader.identity, drafts[1].id, {"quota_size": "60"}
    )
    draft = records_service.read_draft(uploader.identity, drafts[1].id)
    assert draft._record.files.bucket.quota_size == 60 * GB
