# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM PIDs Service tasks."""

from celery import shared_task
from invenio_access.permissions import system_identity

from invenio_rdm_records.proxies import current_rdm_records


@shared_task(ignore_result=True)
def register_or_update_pid(recid, scheme):
    """Update a PID on the remote provider."""
    current_rdm_records.records_service.pids.register_or_update(
        id_=recid,
        identity=system_identity,
        scheme=scheme,
    )
