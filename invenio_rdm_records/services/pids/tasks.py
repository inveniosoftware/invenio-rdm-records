# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Asynchronous tasks for RDM Records PIDs."""

import json
import logging

from celery import shared_task
from datacite import DataCiteRESTClient
from datacite.errors import DataCiteError
from invenio_access.permissions import system_identity

from ...proxies import current_rdm_records
from ...resources.serializers import DataCite43JSONSerializer


def log_errors(errors):
    """Log errors from DataCiteError class."""
    # NOTE: DataCiteError is a tuple with the errors on the first
    errors = json.loads(errors.args[0])["errors"]
    for error in errors:
        field = error["source"]
        reason = error["title"]
        logging.warning(f"Error in {field}: {reason}")


def get_api_client(api_client_name):
    """Get DataCite API client."""
    service = current_rdm_records.records_service

    # instantiate client, not passing it as param to avoid leaking credentials
    client_class = service.config.pids_providers_clients[api_client_name]
    client = client_class(name=api_client_name)

    # instantiate api client
    api_client = DataCiteRESTClient(
        client.username, client.password, client.prefix, client.test_mode
    )

    return api_client


def get_record_data(recid_value):
    """Get record related data needed to interact with DataCite.

    Returns the DataCite JSON serialized metadata of the record, its doi url,
    and the doi value.
    """
    service = current_rdm_records.records_service

    # get record and register doi
    record = service.read(recid_value, system_identity)
    record_dict = record.to_dict()

    doc = DataCite43JSONSerializer().dump_one(record_dict)
    metadata = doc["metadata"]
    url = record_dict["links"]["self_doi"]
    doi = record_dict["pids"]["doi"]["identifier"]

    return metadata, url, doi


@shared_task(ignore_result=True, max_retries=6, default_retry_delay=10 * 60,
             rate_limit='100/m')
def doi_datacite_register(recid_value, api_client_name):
    """Registers a DOI in datacite."""
    api_client = get_api_client(api_client_name)
    metadata, url, doi = get_record_data(recid_value)

    try:
        api_client.public_doi(metadata=metadata, url=url, doi=doi)
    except DataCiteError as e:
        logging.warning("DataCite provider errored when updating " +
                        f"DOI for {recid_value}")
        log_errors(e)


@shared_task(ignore_result=True, max_retries=6, default_retry_delay=10 * 60,
             rate_limit='100/m')
def doi_datacite_update(recid_value, api_client_name):
    """Registers a DOI in datacite."""
    api_client = get_api_client(api_client_name)
    metadata, url, doi = get_record_data(recid_value)

    try:
        api_client.update_doi(metadata=metadata, url=url, doi=doi)
    except DataCiteError as e:
        logging.warning("DataCite provider errored when updating " +
                        f"DOI for {recid_value}")
        log_errors(e)


@shared_task(ignore_result=True, max_retries=6, default_retry_delay=10 * 60,
             rate_limit='100/m')
def doi_datacite_delete(recid_value, doi_value, api_client_name):
    """Registers a DOI in datacite."""
    api_client = get_api_client(api_client_name)

    try:
        api_client.hide_doi(doi_value)
    except DataCiteError as e:
        logging.warning("DataCite provider errored when deleting " +
                        f"DOI for {recid_value}")
        log_errors(e)
