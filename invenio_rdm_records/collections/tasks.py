# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collections celery tasks."""

from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity

from invenio_rdm_records.proxies import current_rdm_records


@shared_task(ignore_result=True)
def update_collections_size():
    """Calculate and update the size of all the collections."""
    collections_service = current_rdm_records.collections_service
    res = collections_service.read_all(system_identity, depth=0)
    for citem in res:
        try:
            collection = citem._collection
            res = collections_service.search_collection_records(
                system_identity, collection
            )
            collections_service.update(
                system_identity, collection, data={"num_records": res.total}
            )
        except Exception as e:
            current_app.logger.exception(str(e))
