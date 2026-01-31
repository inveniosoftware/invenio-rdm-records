# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests record search."""

from invenio_rdm_records.records.api import RDMRecord


def test_advance_record_search(
    client,
    headers,
    record_community,
    minimal_record,
    uploader,
):
    """Test search record's communities."""
    uploader.login(client)

    record_title = "A Römäns storÿ 123456789012"
    minimal_record["metadata"]["title"] = record_title
    record_community.create_record(
        minimal_record, uploader
    )  # Create record without community

    RDMRecord.index.refresh()

    # Search for accent title
    res = client.get("/records", query_string={"q": "romans"}, headers=headers)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    records = res.json["hits"]["hits"]
    assert records[0]["metadata"]["title"] == record_title

    # Search with regex
    res = client.get("/records", query_string={"q": r"/\d{12}/"}, headers=headers)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    records = res.json["hits"]["hits"]
    assert records[0]["metadata"]["title"] == record_title

    # Search with forward slash
    res = client.get("/records", query_string={"q": "/"}, headers=headers)
    assert res.status_code == 200

    # Search with punctuation on title.original subfield (standard)
    res = client.get(
        "/records",
        query_string={"q": "metadata.title.original:romans!%20sto.ry"},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 0

    # Search with punctuation on title field (analyzed)
    res = client.get(
        "/records",
        query_string={"q": "metadata.title:romans!%20sto.ry"},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    records = res.json["hits"]["hits"]
    assert records[0]["metadata"]["title"] == record_title

    uploader.logout(client)
