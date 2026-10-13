# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Tests for StorageService.remaining_storage."""

from invenio_access.permissions import system_identity

from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_rdm_records.proxies import (
    current_rdm_records_storage_service as storage_service,
)

# 5 GB of extra quota per record
EXTRA_QUOTA = 5 * 10**9


def _max_additional_quota(app):
    return app.config["RDM_FILES_DEFAULT_MAX_ADDITIONAL_QUOTA_SIZE"]


def _create_draft_with_extra_quota(
    app, identity, minimal_record, extra_quota=EXTRA_QUOTA
):
    """Create a draft and grant it extra_quota above the default."""
    draft = records_service.create(identity, minimal_record)
    size = app.config["RDM_FILES_DEFAULT_QUOTA_SIZE"] + extra_quota
    records_service.set_quota(
        system_identity,
        draft.id,
        {
            "quota_size": size,
            "max_file_size": size,
        },
    )
    return draft


def _create_published_record_with_extra_quota(
    app, identity, minimal_record, extra_quota=EXTRA_QUOTA
):
    """Create a published record with extra_quota above the default."""
    draft = _create_draft_with_extra_quota(app, identity, minimal_record, extra_quota)
    record = records_service.publish(identity, draft.id)
    return record


def test_remaining_storage_no_records(app, users, location, resource_type_v):
    """With no records, the full additional quota is available."""
    remaining = storage_service.remaining_storage(users[0].id, record=None)
    assert remaining == _max_additional_quota(app)


def test_remaining_storage_published_record(
    app, identity_simple, users, minimal_record, location, resource_type_v
):
    """A published record with allocated quota reduces the remaining storage."""
    _create_published_record_with_extra_quota(app, identity_simple, minimal_record)
    remaining = storage_service.remaining_storage(users[0].id, record=None)
    assert remaining == _max_additional_quota(app) - EXTRA_QUOTA


def test_remaining_storage_draft(
    app, identity_simple, users, minimal_record, location, resource_type_v
):
    """A draft with allocated quota reduces the remaining storage."""
    _create_draft_with_extra_quota(app, identity_simple, minimal_record)
    remaining = storage_service.remaining_storage(users[0].id, record=None)
    assert remaining == _max_additional_quota(app) - EXTRA_QUOTA


def test_remaining_storage_record_deleted(
    app, identity_simple, users, minimal_record, location, resource_type_v
):
    """A parent without published versions should not reduce the remaining storage.

    A parent with allocated quota initially reduces the remaining storage. If its records
    are deleted, and no drafts exist for it, the allocated storage is no longer taken into
    consideration when calculating the remaining storage.
    """
    record = _create_published_record_with_extra_quota(
        app, identity_simple, minimal_record
    )
    draft_v2 = records_service.new_version(identity_simple, record.id)
    record_v2 = records_service.publish(identity_simple, draft_v2.id)
    remaining = storage_service.remaining_storage(users[0].id, record=None)
    assert remaining == _max_additional_quota(app) - EXTRA_QUOTA

    # delete v2
    records_service.delete_record(system_identity, record_v2.id, {})
    remaining = storage_service.remaining_storage(users[0].id, record=None)
    assert remaining == _max_additional_quota(app) - EXTRA_QUOTA

    # delete v1
    records_service.delete_record(system_identity, record.id, {})
    remaining = storage_service.remaining_storage(users[0].id, record=None)
    assert remaining == _max_additional_quota(app)


def test_remaining_storage_record_deleted_active_draft(
    app, identity_simple, users, minimal_record, location, resource_type_v
):
    """A parent with allocated quota, no published records and a draft reduces the remaining storage."""
    record = _create_published_record_with_extra_quota(
        app, identity_simple, minimal_record
    )
    records_service.new_version(identity_simple, record.id)
    remaining = storage_service.remaining_storage(users[0].id, record=None)
    assert remaining == _max_additional_quota(app) - EXTRA_QUOTA


def test_remaining_storage_current_draft(
    app, identity_simple, users, minimal_record, location, resource_type_v
):
    """Correctly calculates a draft's remaining storage.

    A currently-edited draft's extra quota is added back to remaining storage,
    but other drafts' and records' allocated storage reduced the remaining storage.
    """
    draft_1 = _create_draft_with_extra_quota(app, identity_simple, minimal_record)

    # Additional draft and record with allocated storage
    _draft_2 = _create_draft_with_extra_quota(app, identity_simple, minimal_record)
    draft_3 = _create_draft_with_extra_quota(app, identity_simple, minimal_record)
    _record_3 = records_service.publish(identity_simple, draft_3.id)

    draft_obj = records_service.read_draft(identity_simple, draft_1.id)._record
    additional_storage_draft_1 = storage_service.additional_storage(
        users[0].id, record=draft_obj
    )
    assert additional_storage_draft_1 == EXTRA_QUOTA

    remaining_draft_1 = storage_service.remaining_storage(users[0].id, record=draft_obj)
    assert remaining_draft_1 == _max_additional_quota(app) - 2 * EXTRA_QUOTA
