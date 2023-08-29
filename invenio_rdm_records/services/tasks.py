# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks."""

from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.errors import EmbargoNotLiftedError

from invenio_search.engine import dsl, search
from invenio_search.utils import prefix_index
from invenio_search.proxies import current_search_client

@shared_task(ignore_result=True)
def update_expired_embargos():
    """Lift expired embargos."""
    service = current_rdm_records.records_service

    records = service.scan_expired_embargos(system_identity)
    for record in records.hits:
        try:
            service.lift_embargo(_id=record["id"], identity=system_identity)
        except EmbargoNotLiftedError as ex:
            current_app.logger.warning(ex.description)
            continue

@shared_task(ignore_result=True)
def reindex_stats():
    """Reindex the documents where the stats have changed."""
    buffer_index = prefix_index("buffer_stats_to_reindex")
    client = current_search_client
    if not dsl.Index(buffer_index, using=client).exists():
        return
    documents = (
        dsl.Search(
            using=client,
            index=buffer_index,
        )
        .source(includes=["timestamp"])
        .execute()
    )
    latest = None
    all_parents = []
    for doc in documents:
        all_parents.append(doc.meta["id"])
        if not latest or latest < doc.get("timestamp"):
            latest = doc.get("timestamp")
    if not all_parents:
        return
    records_q = dsl.Q("terms", parent__id=all_parents)

    current_rdm_records.records_service.reindex(
        params={"allversions": True},
        identity=system_identity,
        extra_filter=records_q,
    )
    if latest:
        client.delete_by_query(
            index=buffer_index,
            body={"query": {"range": {"timestamp": {"lte": latest}}}},
        )

