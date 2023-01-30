# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-RDM-Records OAI Functionality."""

from datacite import schema43
from flask import current_app, g
from invenio_pidstore.errors import PersistentIdentifierError, PIDDoesNotExistError
from invenio_pidstore.fetchers import FetchedPID
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_search import RecordsSearch
from invenio_search.engine import dsl
from lxml import etree

from .proxies import current_rdm_records
from .resources.serializers.datacite import DataCite43XMLSerializer
from .resources.serializers.dublincore import DublinCoreXMLSerializer
from .resources.serializers.marcxml import MARCXMLSerializer
from .services.pids.providers.oai import OAIPIDProvider


def dublincore_etree(pid, record):
    """Get DublinCore XML etree for OAI-PMH."""
    return DublinCoreXMLSerializer().serialize_object_xml(record["_source"])


def oai_marcxml_etree(pid, record):
    """OAI MARCXML format for OAI-PMH.

    It assumes that record is a search result.
    """
    return etree.fromstring(MARCXMLSerializer().serialize_object(record["_source"]))


def datacite_etree(pid, record):
    """DataCite XML format for OAI-PMH.

    It assumes that record is a search result.
    """
    data_dict = DataCite43XMLSerializer().dump_one(record["_source"])
    return schema43.dump_etree(data_dict)


def oai_datacite_etree(pid, record):
    """OAI DataCite XML format for OAI-PMH.

    It assumes that record is a search result.
    """
    resource_dict = DataCite43XMLSerializer().dump_one(record["_source"])

    nsmap = {
        None: "http://schema.datacite.org/oai/oai-1.1/",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    attribs = {
        f"{{{nsmap['xsi']}}}schemaLocation": (
            "http://schema.datacite.org/oai/oai-1.1/ "
            "http://schema.datacite.org/oai/oai-1.1/oai.xsd"
        ),
    }

    # prepare the structure required by the 'oai_datacite' metadataPrefix
    oai_datacite = etree.Element("oai_datacite", nsmap=nsmap, attrib=attribs)
    schema_version = etree.SubElement(oai_datacite, "schemaVersion")
    datacentre_symbol = etree.SubElement(oai_datacite, "datacentreSymbol")
    payload = etree.SubElement(oai_datacite, "payload")

    # dump the record's metadata as usual
    resource = schema43.dump_etree(resource_dict)
    payload.append(resource)

    # set up the elements' contents
    schema_version.text = "4.3"
    datacentre_symbol.text = current_app.config.get("DATACITE_DATACENTER_SYMBOL")

    return oai_datacite


def oaiid_fetcher(record_uuid, data):
    """Fetch a record's identifier.

    :param record_uuid: The record UUID.
    :param data: The record data.
    :returns: A :class:`invenio_pidstore.fetchers.FetchedPID` instance.
    """
    pid_value = data.get("pids", {}).get("oai", {}).get("identifier")
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
        pid_type="recid", object_uuid=record_id, object_type="rec"
    )

    try:
        result = current_rdm_records.records_service.read(g.identity, recid.pid_value)
    except PermissionDeniedError:
        # if it is a restricted record.
        raise PIDDoesNotExistError("recid", None)

    return result.to_dict()


class OAIRecordSearch(RecordsSearch):
    """Define default filter for quering OAI server."""

    class Meta:
        """Configuration for OAI server search."""

        default_filter = [
            dsl.Q("exists", field="pids.oai.identifier"),
            dsl.Q("term", **{"access.record": "public"}),
        ]
