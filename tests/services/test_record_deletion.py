# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Service-level tests for record deletion."""

from copy import deepcopy
from datetime import datetime

import arrow
import pytest

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records.api import RDMRecord
from invenio_rdm_records.records.systemfields.deletion_status import (
    RecordDeletionStatusEnum,
)
from invenio_rdm_records.services.errors import DeletionStatusException


def assert_parent_resolved_to_record(
    service, identity, parent_pid, record, status=RecordDeletionStatusEnum.PUBLISHED
):
    """."""
    # resolve parent pid to latest
    resolved_rec = service.pids.resolve(identity, parent_pid, "recid")
    assert resolved_rec._record.pid.pid_value == record._record.pid.pid_value
    assert resolved_rec._obj.deletion_status == status


def test_record_deletion(running_app, minimal_record, search_clear):
    """Test simple record deletion of a record."""
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(superuser_identity, draft.id)

    assert record._obj.deletion_status == RecordDeletionStatusEnum.PUBLISHED

    # delete the record
    tombstone_info = {"note": "no specific reason, tbh"}
    record = service.delete_record(superuser_identity, record.id, tombstone_info)
    tombstone = record._obj.tombstone

    # check if the tombstone information got added as expected
    assert record._record.deletion_status == RecordDeletionStatusEnum.DELETED
    assert tombstone.is_visible
    assert tombstone.removed_by == {"user": str(superuser_identity.id)}
    assert tombstone.removal_reason is None
    assert tombstone.note == tombstone_info["note"]
    assert tombstone.citation_text
    assert arrow.get(tombstone.removal_date).date() == datetime.utcnow().date()

    # mark the record for purge
    record = service.mark_record_for_purge(superuser_identity, record.id)
    assert record._obj.deletion_status == RecordDeletionStatusEnum.MARKED
    assert record._obj.deletion_status.is_deleted
    assert record._obj.tombstone is not None

    # remove the mark again, we don't wanna purge it after all
    record = service.unmark_record_for_purge(superuser_identity, record.id)
    assert record._obj.deletion_status == RecordDeletionStatusEnum.DELETED
    assert record._obj.deletion_status.is_deleted
    assert record._obj.tombstone is not None

    # restore the record, it wasn't so bad after all
    record = service.restore_record(superuser_identity, record.id)
    assert record._obj.deletion_status == RecordDeletionStatusEnum.PUBLISHED
    assert not record._obj.deletion_status.is_deleted
    assert record._obj.tombstone is None


def test_invalid_record_deletion_workflows(running_app, minimal_record, search_clear):
    """Test the wrong order of deletion operations."""
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(superuser_identity, draft.id)

    assert record._obj.deletion_status == RecordDeletionStatusEnum.PUBLISHED

    # we cannot restore a published record
    with pytest.raises(DeletionStatusException):
        service.restore_record(superuser_identity, record.id)

    # we cannot mark a published record for purge
    with pytest.raises(DeletionStatusException):
        service.mark_record_for_purge(superuser_identity, record.id)

    # we cannot unmark a published record
    with pytest.raises(DeletionStatusException):
        service.unmark_record_for_purge(superuser_identity, record.id)

    record = service.delete_record(superuser_identity, record.id, {})
    assert record._obj.deletion_status == RecordDeletionStatusEnum.DELETED

    # we cannot unmark a deleted record
    with pytest.raises(DeletionStatusException):
        service.unmark_record_for_purge(superuser_identity, record.id)

    record = service.mark_record_for_purge(superuser_identity, record.id)
    assert record._obj.deletion_status == RecordDeletionStatusEnum.MARKED

    # we cannot directly restore a record marked for purge
    with pytest.raises(DeletionStatusException):
        service.restore_record(superuser_identity, record.id)


def test_record_deletion_of_specific_version(running_app, minimal_record, search_clear):
    """Test record deletion of a specific version."""
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    draft = service.create(superuser_identity, minimal_record)
    record_v1 = service.publish(superuser_identity, draft.id)
    published_parent_pid = record_v1._record.parent.pid.pid_value

    # publish v2
    minimal_record_v2 = deepcopy(minimal_record)
    minimal_record_v2["metadata"]["title"] = f"{minimal_record['metadata']['title']} v2"
    draft_v2 = service.new_version(superuser_identity, record_v1.id)
    service.update_draft(superuser_identity, draft_v2.id, minimal_record_v2)
    record_v2 = service.publish(superuser_identity, draft_v2.id)

    assert record_v2._obj.deletion_status == RecordDeletionStatusEnum.PUBLISHED

    # resolve parent pid to record v2
    assert_parent_resolved_to_record(
        service, superuser_identity, published_parent_pid, record_v2
    )

    # search
    res = service.search(
        superuser_identity,
        params={
            "status": RecordDeletionStatusEnum.PUBLISHED.value,
            "allversions": True,
        },
    )
    assert res.total == 2

    # delete the record v1
    tombstone_info = {"note": "no specific reason, tbh"}
    record = service.delete_record(superuser_identity, record_v1.id, tombstone_info)

    # resolve parent pid to record v1
    assert_parent_resolved_to_record(
        service, superuser_identity, published_parent_pid, record_v2
    )

    RDMRecord.index.refresh()

    # search
    res = service.search(
        superuser_identity,
        params={
            "status": RecordDeletionStatusEnum.PUBLISHED.value,
            "allversions": True,
        },
    )
    assert res.total == 1

    # delete the record v2
    tombstone_info = {"note": "no specific reason, tbh"}
    record = service.delete_record(superuser_identity, record_v2.id, tombstone_info)
    tombstone = record._obj.tombstone

    # resolve parent pid to record v2 but deleted (v2 was the last version)
    assert_parent_resolved_to_record(
        service,
        superuser_identity,
        published_parent_pid,
        record_v2,  # resolved rec
        status=RecordDeletionStatusEnum.DELETED,
    )
    assert tombstone.note == tombstone_info["note"]

    RDMRecord.index.refresh()

    # search
    res = service.search(
        superuser_identity,
        params={
            "status": RecordDeletionStatusEnum.PUBLISHED.value,
            "allversions": True,
        },
    )
    assert res.total == 0

    # restore the record v1
    record = service.restore_record(superuser_identity, record_v1.id)
    assert record._obj.deletion_status == RecordDeletionStatusEnum.PUBLISHED
    assert not record._obj.deletion_status.is_deleted
    assert record._obj.tombstone is None

    # resolve parent pid to record v1
    assert_parent_resolved_to_record(
        service, superuser_identity, published_parent_pid, record_v1
    )

    RDMRecord.index.refresh()

    # search
    res = service.search(
        superuser_identity,
        params={
            "status": RecordDeletionStatusEnum.PUBLISHED.value,
            "allversions": True,
        },
    )
    assert res.total == 1

    # create new version from restored v1
    minimal_record_v2 = deepcopy(minimal_record)
    minimal_record_v2["metadata"]["title"] = f"{minimal_record['metadata']['title']} v3"
    draft_v3 = service.new_version(superuser_identity, record_v1.id)
    service.update_draft(superuser_identity, draft_v3.id, minimal_record_v2)
    record_v3 = service.publish(superuser_identity, draft_v3.id)

    # resolve parent pid to record v3
    assert_parent_resolved_to_record(
        service, superuser_identity, published_parent_pid, record_v3
    )

    RDMRecord.index.refresh()

    # search
    res = service.search(
        superuser_identity,
        params={
            "status": RecordDeletionStatusEnum.PUBLISHED.value,
            "allversions": True,
        },
    )
    assert res.total == 2

    # restore the record v2
    record = service.restore_record(superuser_identity, record_v2.id)
    assert record._obj.deletion_status == RecordDeletionStatusEnum.PUBLISHED
    assert not record._obj.deletion_status.is_deleted
    assert record._obj.tombstone is None

    # resolve parent pid to record v3
    assert_parent_resolved_to_record(
        service, superuser_identity, published_parent_pid, record_v3
    )

    RDMRecord.index.refresh()

    # search
    res = service.search(
        superuser_identity,
        params={
            "status": RecordDeletionStatusEnum.PUBLISHED.value,
            "allversions": True,
        },
    )

    assert res.total == 3
    hits = [(hit["id"], hit["versions"]["index"]) for hit in res.hits]
    # assert the correct order of (id, version.index)
    assert hits[0] == (record_v3.id, 3)
    assert hits[1] == (record_v2.id, 2)
    assert hits[2] == (record_v1.id, 1)
