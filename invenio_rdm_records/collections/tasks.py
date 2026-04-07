# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Collections celery tasks."""

from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_db import db
from ..proxies import current_community_collections_service


@shared_task(ignore_result=True)
def update_collections_size():
    """Calculate and update the size of all the collections."""
    res = current_community_collections_service.read_all(system_identity, depth=0)
    for citem in res:
        try:
            collection = citem._collection
            res = current_community_collections_service.search_collection_records(
                system_identity, collection
            )
            collection.update(num_records=res.total)
            db.session.commit()
        except Exception as e:
            current_app.logger.exception(str(e))
