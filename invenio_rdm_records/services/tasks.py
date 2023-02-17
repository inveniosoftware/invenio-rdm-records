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
from invenio_db import db
from invenio_indexer.api import RecordIndexer

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records import RDMRecord, models
from invenio_rdm_records.services.errors import EmbargoNotLiftedError


@shared_task(ignore_result=True)
def update_expired_embargos():
    """Lift expired embargos."""
    service = current_rdm_records.records_service

    records = service.scan_expired_embargos(system_identity)
    for record in records.hits:
        try:
            service.lift_embargo(_id=record["id"], identity=system_identity)
        except EmbargoNotLiftedError:
            current_app.logger.warning(
                f"Embargo from record with id {record['id']} was not lifted"
            )
            continue


@shared_task
def remove_community_from_records(community_id, delay=True):
    """Removes all the records from the community."""
    try:
        record_communities = models.RDMParentCommunity.query.filter_by(
            community_id=community_id
        ).all()
        for record_community in record_communities:
            if delay:
                remove_community_from_record.delay(
                    str(record_community.record_id), community_id
                )
            else:
                remove_community_from_record(
                    str(record_community.record_id), community_id
                )
    except Exception as e:
        current_app.logger.error(
            f"Error on removing records from the following community: {community_id}\nError details: {e}"
        )


@shared_task
def remove_community_from_record(record_id, community_id):
    """Remove the community from the record."""
    try:
        parent = RDMRecord.parent_record_cls.get_record(record_id)

        records = RDMRecord.get_records_by_parent(parent)
        for record in records:
            record.parent.communities.remove(community_id)
            record.parent.commit()
            db.session.commit()
            RecordIndexer().index(record)

    except Exception as e:
        current_app.logger.error(
            f"Error on removing the record {record_id} from community {community_id}\nError details: {e}"
        )
