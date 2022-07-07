# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Affiliation resource tests."""

import pytest
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.affiliations.api import Affiliation


@pytest.fixture(scope="module")
def affiliations_service():
    return current_service_registry.get("affiliations")


@pytest.fixture()
def example_affiliation(
    app, db, search_clear, superuser_identity, affiliations_service
):
    """Example affiliation."""
    data = {
        "acronym": "TEST",
        "id": "cern",
        "identifiers": [{"identifier": "03yrm5c26", "scheme": "ror"}],
        "name": "Test affiliation",
        "title": {"en": "Test affiliation", "es": "Afiliacion de test"},
    }
    aff = affiliations_service.create(superuser_identity, data)
    Affiliation.index.refresh()  # Refresh the index

    yield aff

    affiliations_service.delete(superuser_identity, aff.id)


def test_affiliations_get(client, example_affiliation, headers):
    """Test the endpoint to retrieve a single item."""
    id_ = example_affiliation.id

    res = client.get(f"/affiliations/{id_}", headers=headers)
    assert res.status_code == 200
    assert res.json["id"] == id_
    # Test links
    assert res.json["links"] == {"self": "https://127.0.0.1:5000/api/affiliations/cern"}


def test_affiliations_search(client, example_affiliation, headers):
    """Test a successful search."""
    res = client.get("/affiliations", headers=headers)

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["sortBy"] == "name"
