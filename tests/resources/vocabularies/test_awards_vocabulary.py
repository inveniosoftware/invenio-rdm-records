# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Award resource tests."""

import pytest
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.awards.api import Award


@pytest.fixture(scope="module")
def awards_service():
    return current_service_registry.get("rdm-awards")


@pytest.fixture()
def example_award(
    app, db, es_clear, superuser_identity, awards_service
):
    """Example award."""
    data = {
        "pid": "755021",
        "identifiers": [
            {
                "identifier": "https://cordis.europa.eu/project/id/755021",
                "scheme": "url"
            }
        ],
        "number": "755021",
        "title": {
            "en": "Personalised Treatment For Cystic Fibrosis Patients With \
                Ultra-rare CFTR Mutations (and beyond)",
        },
        "funder": {
            # FIXME: add appropriate value when funders has been integrated
            "id": "0....."
        }
    }
    awa = awards_service.create(superuser_identity, data)
    Award.index.refresh()  # Refresh the index

    yield awa

    awards_service.delete(superuser_identity, awa.id)


def test_awards_get(client, example_award, headers):
    """Test the endpoint to retrieve a single item."""
    id_ = example_award.id

    res = client.get(f"/awards/{id_}", headers=headers)
    assert res.status_code == 200
    assert res.json["pid"] == id_
    # Test links
    assert res.json["links"] == {
        "self": "https://127.0.0.1:5000/api/awards/755021"
    }


def test_awards_search(client, example_award, headers):
    """Test a successful search."""
    res = client.get("/awards", headers=headers)

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["sortBy"] == "newest"
    assert res.json["aggregations"]["funders"]

    funders_agg = res.json["aggregations"]["funders"]["buckets"][0]
    assert funders_agg["key"] == "01ggx4157"
    assert funders_agg["doc_count"] == 1
    assert funders_agg["label"] == \
        "European Organization for Nuclear Research (CH)"
