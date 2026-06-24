# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-License-Identifier: MIT

"""RDM PIDs Service tasks."""

from copy import copy, deepcopy

from celery import shared_task
from invenio_access.permissions import system_identity
from invenio_records_resources.services.uow import TaskOp, unit_of_work

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
    parent_pids = copy(record.parent.get("pids", {}))
    if record.deleted:
        parent_pids = deepcopy(record.parent.get("pids", {}))
        if record_cls.next_latest_published_record_by_parent(record.parent) is None:
            record_cls.pids.parent_pid_manager.discard_all(
                parent_pids, soft_delete=True
            )

    @unit_of_work()
    def send_register_or_update_pid(recid, scheme, uow=None):
        uow.register(TaskOp(register_or_update_pid, recid, scheme, parent=True))

    # Async register/update tasks
    for scheme in parent_pids.keys():
        send_register_or_update_pid(record["id"], scheme)
