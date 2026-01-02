# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""User moderation tasks."""

from celery import shared_task
from invenio_access.permissions import system_identity
from invenio_users_resources.records.api import UserAggregate

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.systemfields.deletion_status import (
    RecordDeletionStatusEnum,
)
from invenio_rdm_records.services.errors import DeletionStatusException

from .utils import get_user_records


@shared_task(ignore_result=True)
def user_block_cleanup(user_id, tombstone_data):
    """User block action cleanup."""
    user = UserAggregate.get_record(user_id)
    # Bail out if the user is not blocked (i.e. we restored him before the task ran)
    if not user.blocked:
        return

    for recid in get_user_records(
        user_id,
        from_db=True,
        # Only fetch published records that might have not been deleted yet.
        status=[RecordDeletionStatusEnum.PUBLISHED],
    ):
        delete_record.delay(recid, tombstone_data)


@shared_task(ignore_result=True)
def user_restore_cleanup(user_id):
    """User restore action cleanup."""
    user = UserAggregate.get_record(user_id)
    # Bail out if the user is blocked (i.e. we blocked him before the task ran)
    if user.blocked:
        return

    for recid in get_user_records(
        user_id,
        from_db=True,
        # Only fetch deleted records that might have not been restored yet.
        status=[RecordDeletionStatusEnum.DELETED],
    ):
        restore_record.delay(recid)


@shared_task(ignore_result=True)
def delete_record(recid, tombstone_data):
    """Delete a single record."""
    try:
        current_rdm_records_service.delete_record(
            system_identity, recid, tombstone_data
        )
    except DeletionStatusException as ex:
        # Record is already deleted; index it again to make sure search is up-to-date.
        current_rdm_records_service.indexer.index(ex.record)


@shared_task(ignore_result=True)
def restore_record(recid):
    """Restore a single record."""
    try:
        current_rdm_records_service.restore_record(system_identity, recid)
    except DeletionStatusException as ex:
        # Record is already restored; index it again to make sure search is up-to-date.
        current_rdm_records_service.indexer.index(ex.record)
