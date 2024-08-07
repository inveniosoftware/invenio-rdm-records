# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""User moderation tasks."""

from celery import shared_task
from invenio_access.permissions import system_identity

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.services.errors import DeletionStatusException


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
