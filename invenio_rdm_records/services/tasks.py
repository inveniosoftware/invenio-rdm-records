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
from invenio_records_resources.proxies import current_service_registry


@shared_task(ignore_result=True)
def update_expired_embargos():
    """Lift expired embargos."""
    service = current_rdm_records.records_service

    records = service.scan_expired_embargos(system_identity)
    for record in records.hits:
        try:
            service.lift_embargo(_id=record['id'], identity=system_identity)
        except EmbargoNotLiftedError:
            current_app.logger.warning(
                f"Embargo from record with id {record['id']} was not lifted")
            continue


@shared_task(ignore_result=True)
def propagate_updated_vocabularies(type, records):
    """Propagates the update of vocabulary records to bibliographic reocrds.

    :param type: vocabulary type, necessary to pick the service.
    :param records: vocabulary records that were updated.
    """
    task_start = arrow.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")
    service = current_service_registry.get(type)
    build_query() # we need the UUID and the version_id of each record

    # Q: We could do a scan() and use the indexer from here.
    # avoiding an extra step for the service.reindex + queue/consumption
    # Does this bypass preparing the record? I think not.

