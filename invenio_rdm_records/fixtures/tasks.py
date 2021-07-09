# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks for fixtures."""
from celery import shared_task
from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.proxies import current_service as vocabulary_service

from ..proxies import current_rdm_records


@shared_task
def create_vocabulary_record(service_str, data):
    """Create a vocabulary record."""
    # NiceTodo: current_service_registry should have an interface like a dict
    if service_str == "vocabulary_service":
        service = vocabulary_service
    else:
        service = current_service_registry.get(service_str)
    service.create(system_identity, data)


@shared_task
def create_demo_record(data):
    """Create a demo record."""
    service = current_rdm_records.records_service
    draft = service.create(data=data, identity=system_identity)
    service.publish(id_=draft.id, identity=system_identity)
