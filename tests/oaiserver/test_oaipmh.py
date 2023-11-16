# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the OAI-PMH endpoint."""

import itertools

from flask import url_for


def test_identify(running_app, client, search_clear):
    """Test the OAI-PMH Identify verb."""
    resp = client.get(url_for("invenio_oaiserver.response", verb="Identify"))
    assert resp.status_code == 200
    assert "<repositoryName>InvenioRDM</repositoryName>" in resp.text
    assert "<baseURL>http://localhost/oai2d</baseURL>" in resp.text
    assert "<protocolVersion>2.0</protocolVersion>" in resp.text
    assert "<adminEmail>info@inveniosoftware.org</adminEmail>" in resp.text
    assert "<earliestDatestamp>0001-01-01T00:00:00Z</earliestDatestamp>" in resp.text
    assert "<deletedRecord>no</deletedRecord>" in resp.text
    assert "<granularity>YYYY-MM-DDThh:mm:ssZ</granularity>" in resp.text


def test_list_sets(running_app, client, community, search_clear):
    """Test the OAI-PMH ListSets verb."""
    resp = client.get(url_for("invenio_oaiserver.response", verb="ListSets"))
    assert resp.status_code == 200
    assert "<setSpec>community-blr</setSpec>" in resp.text
    assert "<setName>Biodiversity Literature Repository</setName>" in resp.text
    assert "<setDescription>" in resp.text
    assert (
        "<dc:description>Records belonging to the community "
        "'Biodiversity Literature Repository'</dc:description>"
    ) in resp.text


def test_harvest(running_app, client, record_factory, search_clear):
    """Test the OAI-PMH ListIdentifiers verb."""
    metadata_formats = running_app.app.config["OAISERVER_METADATA_FORMATS"].keys()
    verbs = ["ListIdentifiers", "ListRecords"]
    oai_sets = [None, "community-blr"]
    url_params = itertools.product(verbs, metadata_formats, oai_sets)

    def _build_oai_url(verb, metadata_format, oai_set=None, identifier=None):
        params = {"verb": verb, "metadataPrefix": metadata_format}
        if oai_set:
            params["set"] = oai_set
        if identifier:
            params["identifier"] = identifier
        return url_for("invenio_oaiserver.response", **params)

    for verb, metadata_format, oai_set in url_params:
        url = _build_oai_url(verb, metadata_format, oai_set)
        resp = client.get(url)
        assert resp.status_code == 422
        assert '<error code="noRecordsMatch"></error></OAI-PMH>' in resp.text

    # Create two records, one with a community and one without
    no_community_record = record_factory.create_record(community=None, file="test.txt")
    community_record = record_factory.create_record(file="test.txt")

    for verb, metadata_format, oai_set in url_params:
        url = _build_oai_url(verb, metadata_format, oai_set)
        resp = client.get(url)
        assert resp.status_code == 200
        if oai_set:
            assert (
                f"<identifier>oai:inveniordm:{no_community_record['id']}</identifier>"
                not in resp.text
            )
        else:
            assert (
                f"<identifier>oai:inveniordm:{no_community_record['id']}</identifier>"
                in resp.text
            )
        assert (
            f"<identifier>oai:inveniordm:{community_record['id']}</identifier>"
            in resp.text
        )

    for metadata_format, record in itertools.product(
        metadata_formats,
        [no_community_record, community_record],
    ):
        oai_id = f"oai:inveniordm:{record['id']}"
        url = _build_oai_url("GetRecord", metadata_format, identifier=oai_id)
        resp = client.get(url)
        assert resp.status_code == 200
        assert f"<identifier>{oai_id}</identifier>" in resp.text
        if record["id"] == community_record["id"]:
            assert "<setSpec>community-blr</setSpec>" in resp.text
