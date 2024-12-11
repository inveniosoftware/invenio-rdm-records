# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM PIDs Service tasks."""

from copy import deepcopy

from celery import shared_task
from invenio_access.permissions import system_identity

from ...proxies import current_rdm_records


@shared_task(ignore_result=True)
def register_or_update_pid(recid, scheme, parent=False):
    """Update a PID on the remote provider."""
    current_rdm_records.records_service.pids.register_or_update(
        id_=recid,
        identity=system_identity,
        scheme=scheme,
        parent=parent,
    )


@shared_task(ignore_result=True)
def cleanup_parent_pids(recid):
    """Clean up parent PIDs."""
    record_cls = current_rdm_records.records_service
    record = record_cls.pid.resolve(recid, with_deleted=True)
    if record.deleted:
        parent_pids = deepcopy(record.parent.get("pids", {}))
        if record_cls.next_latest_published_record_by_parent(record.parent) is None:
            record_cls.pids.parent_pid_manager.discard_all(
                parent_pids, soft_delete=True
            )
