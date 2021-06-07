# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks."""
import arrow
from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.errors import EmbargoNotLiftedError


@shared_task(ignore_result=True)
def update_expired_embargos():
    """Release expired embargoes."""
    service = current_rdm_records.records_service
    embargoed_q = "access.embargo.active:true AND access.embargo.until:" \
                  f"{{* TO {arrow.utcnow().datetime.strftime('%Y-%m-%d')}}}"
    # Retrieve overdue embargoed records
    restricted_records = service.scan(identity=system_identity, q=embargoed_q)
    for restricted_record in restricted_records.hits:
        try:
            service.lift_embargo(
                _id=restricted_record['id'],
                identity=system_identity
            )
        except EmbargoNotLiftedError:
            current_app.logger.warning("Embargo from record with id"
                                       f" {restricted_record['id']} was not"
                                       " lifted")
            continue
