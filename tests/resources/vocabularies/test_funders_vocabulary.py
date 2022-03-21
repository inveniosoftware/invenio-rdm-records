# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Funder resource tests."""

import pytest
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.funders.api import Funder


@pytest.fixture(scope="module")
def funders_service():
    return current_service_registry.get("rdm-funders")


@pytest.fixture()
def example_funder(
    app, db, es_clear, superuser_identity, funders_service
):
    """Example funder."""
    data = {
        "pid": "01ggx4157",
        "identifiers": [
            {"identifier": "01ggx4157", "scheme": "ror"}
        ],
        "name": "CERN",
        "title": {
            "en": "European Organization for Nuclear Research",
        }
    }
    fun = funders_service.create(superuser_identity, data)
    Funder.index.refresh()  # Refresh the index

    yield fun

    funders_service.delete(superuser_identity, fun.id)


def test_funders_get(client, example_funder, headers):
    """Test the endpoint to retrieve a single item."""
    id_ = example_funder.id

    res = client.get(f"/funders/{id_}", headers=headers)
    assert res.status_code == 200
    assert res.json["pid"] == id_
    # Test links
    assert res.json["links"] == {
        "self": "https://127.0.0.1:5000/api/funders/01ggx4157"
    }


def test_funders_search(client, example_funder, headers):
    """Test a successful search."""
    res = client.get("/funders", headers=headers)

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["sortBy"] == "name"
