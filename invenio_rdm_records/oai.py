# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-RDM-Records OAI Functionality."""

from elasticsearch_dsl import Q
from flask import g
from invenio_pidstore.errors import PersistentIdentifierError, \
    PIDDoesNotExistError
from invenio_pidstore.fetchers import FetchedPID
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_search import RecordsSearch

from .proxies import current_rdm_records
from .resources.serializers.dublincore import DublinCoreXMLSerializer
from .services.pids.providers.oai import OAIPIDProvider


def dublincore_etree(pid, record):
    """Get DublinCore XML etree for OAI-PMH."""
    return DublinCoreXMLSerializer().serialize_object_xml(record["_source"])


def oaiid_fetcher(record_uuid, data):
    """Fetch a record's identifier.

    :param record_uuid: The record UUID.
    :param data: The record data.
    :returns: A :class:`invenio_pidstore.fetchers.FetchedPID` instance.
    """
    pid_value = data.get('pids', {}).get('oai', {}).get('identifier')
    if pid_value is None:
        raise PersistentIdentifierError()

    return FetchedPID(
        provider=OAIPIDProvider,
        pid_type="oai",
        pid_value=str(pid_value),
    )


def getrecord_fetcher(record_id):
    """Fetch record data as dict with identity check for serialization."""
    recid = PersistentIdentifier.get_by_object(
        pid_type='recid', object_uuid=record_id, object_type='rec'
    )

    try:
        result = current_rdm_records.records_service.read(
            recid.pid_value, g.identity
        )
    except PermissionDeniedError:
        # if it is a restricted record.
        raise PIDDoesNotExistError('recid', None)

    return result.to_dict()


class OAIRecordSearch(RecordsSearch):
    """Define default filter for quering OAI server."""

    class Meta:
        """Configuration for OAI server search."""

        default_filter = [
            Q('exists', field='pids.oai.identifier'),
            Q('term', **{'access.record': 'public'}),
        ]
