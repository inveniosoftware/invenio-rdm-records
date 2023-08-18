# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Service-level tests for record deletion."""

from datetime import datetime

import arrow
import pytest
from invenio_access.permissions import system_identity

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records.systemfields.deletion_status import (
    RecordDeletionStatusEnum,
)
from invenio_rdm_records.services.errors import DeletionStatusException


def test_record_deletion(running_app, minimal_record):
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


def test_invalid_record_deletion_workflows(running_app, minimal_record):
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
