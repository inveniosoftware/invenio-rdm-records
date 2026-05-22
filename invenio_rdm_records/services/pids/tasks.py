# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-License-Identifier: MIT

"""RDM PIDs Service tasks."""

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
