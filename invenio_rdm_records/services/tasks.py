# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2025-2026 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks."""

import math
from datetime import datetime, timedelta, timezone

from celery import shared_task
from celery.schedules import crontab
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_search.engine import dsl
from invenio_search.proxies import current_search_client
from invenio_search.utils import prefix_index
from invenio_stats.bookmark import BookmarkAPI

from invenio_rdm_records.services.signals import post_publish_signal

from ..proxies import current_rdm_records
from .errors import EmbargoNotLiftedError

# runs every hour at minute 10 for a consistent offset from process and aggregate
# event statistics.
StatsRDMReindexTask = {
    "task": "invenio_rdm_records.services.tasks.reindex_stats",
    "schedule": crontab(minute="05,15,25,35,45,55"),  # crontab(minute=10),
    "args": [
        (
            "stats-record-view",
            "stats-file-download",
        )
    ],
}


@shared_task(ignore_result=True)
def update_expired_embargos():
    """Lift expired embargos."""
    current_app.logger.debug("Updating expired embargoes")
    service = current_rdm_records.records_service

    records = service.scan_expired_embargos(system_identity)
    lifted_embargoes = 0
    for record in records.hits:
        try:
            current_app.logger.info(f"Lifting embargo for record {record['id']}")
            service.lift_embargo(_id=record["id"], identity=system_identity)
            lifted_embargoes += 1
        except EmbargoNotLiftedError as ex:
            current_app.logger.warning(ex.description)
            continue
    current_app.logger.info(f"Lifted {lifted_embargoes} embargoes")


@shared_task(ignore_result=True)
def reindex_stats(stats_indices):
    """Reindex the documents where the stats have changed."""
    bm = BookmarkAPI(current_search_client, "stats_reindex", "day")
    last_run = bm.get_bookmark()
    if not last_run:
        # If this is the first time that we run, let's do it for the documents of the last week
        last_run = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    reindex_start_time = datetime.now(timezone.utc).isoformat()
    indices = ",".join(map(lambda x: prefix_index(x) + "*", stats_indices))

    all_parents = set()
    query = dsl.Search(
        using=current_search_client,
        index=indices,
    ).filter({"range": {"updated_timestamp": {"gte": last_run}}})

    for result in query.scan():
        parent_id = result.parent_recid
        all_parents.add(parent_id)

    if all_parents:
        all_parents_list = list(all_parents)
        step = 10000
        end = len(list(all_parents))
        for i in range(0, end, step):
            records_q = dsl.Q("terms", parent__id=all_parents_list[i : i + step])
            current_rdm_records.records_service.reindex(
                params={"allversions": True},
                identity=system_identity,
                search_query=records_q,
            )
    bm.set_bookmark(reindex_start_time)
    return "%d documents reindexed" % len(all_parents)


@shared_task(ignore_result=True)
def send_post_published_signal(pid):
    """Sends a signal for a published record."""
    post_publish_signal.send(current_app._get_current_object(), pid=pid)
