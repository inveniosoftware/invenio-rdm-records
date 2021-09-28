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
def register_pid(pid_type, pid_value, recid, provider_name=None):
    """Registers a PID."""
    provider = current_rdm_records.records_service.pids.get_provider(
        pid_type, provider_name
    )
    pid = provider.get(pid_value=pid_value, pid_type=pid_type)
    record = current_rdm_records.records_service.read(
        recid, system_identity
    )
    provider.register(
        pid, record=record._record, url=record.to_dict()["links"]["self_html"]
    )
    db.session.commit()
