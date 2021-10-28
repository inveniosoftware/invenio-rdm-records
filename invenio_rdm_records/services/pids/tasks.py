# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM PIDs Service tasks."""

from celery import shared_task
from invenio_access.permissions import system_identity
from invenio_db import db

from invenio_rdm_records.proxies import current_rdm_records


@shared_task(ignore_result=True)
def update_pid(recid, pid_type):
    """Update a PID on the remote provider."""
    current_rdm_records.records_service.pids.update_remote(
        id_=recid,
        identity=system_identity,
        scheme=pid_type,
    )


@shared_task(ignore_result=True)
def register_pid(recid, pid_type):
    """Registers a PID of a record."""
    current_rdm_records.records_service.pids.register(
        id_=recid,
        identity=system_identity,
        scheme=pid_type,
    )
