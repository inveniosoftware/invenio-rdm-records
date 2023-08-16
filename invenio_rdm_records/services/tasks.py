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
from invenio_i18n import lazy_gettext as _
from invenio_requests.proxies import current_user_moderation_service
from invenio_requests.services.user_moderation.errors import OpenRequestAlreadyExists

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.errors import EmbargoNotLiftedError


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
def request_moderation_async(user_id):
    """Creates a task to request moderation for a user.

    Why this task: when a record is published, we want to request moderation for a user.
    However, the moderation service might implement heavier operations (e.g. querying) and we don't want to delay the publishing of the record.

    """
    try:
        current_user_moderation_service.request_moderation(
            system_identity, user_id=user_id
        )
    except OpenRequestAlreadyExists as ex:
        current_app.logger.warning(ex.description)
