# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-RDM-Records OAI Functionality."""

from elasticsearch_dsl import Q
from invenio_pidstore.errors import PersistentIdentifierError
from invenio_pidstore.fetchers import FetchedPID
from invenio_search import RecordsSearch

from .services.pids.providers.oai import OAIPIDProvider


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


class OAIRecordSearch(RecordsSearch):
    """Define default filter for quering OAI server."""

    class Meta:
        """Configuration for OAI server search."""

        default_filter = Q('exists', field='pids.oai.identifier')
