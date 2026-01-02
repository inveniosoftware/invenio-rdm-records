# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Name resource tests."""

import pytest
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.names.api import Name


@pytest.fixture(scope="module")
def names_service():
    return current_service_registry.get("names")


@pytest.fixture()
def example_name(app, db, search_clear, superuser_identity, names_service):
    """Example name."""
    data = {
        "id": "0000-0001-8135-3489",
        "name": "Doe, John",
        "given_name": "John",
        "family_name": "Doe",
        "identifiers": [
            {"identifier": "0000-0001-8135-3489", "scheme": "orcid"},
            {"identifier": "gnd:4079154-3", "scheme": "gnd"},
        ],
        "affiliations": [{"name": "CustomORG"}],
    }
    name = names_service.create(superuser_identity, data)
    Name.index.refresh()  # Refresh the index

    yield name

    names_service.delete(superuser_identity, name.id)


def test_names_get(client_with_login, example_name, headers):
    """Test the endpoint to retrieve a single item."""
    id_ = example_name.id

    res = client_with_login.get(f"/names/{id_}", headers=headers)
    assert res.status_code == 200
    assert res.json["id"] == id_
    # Test links
    assert res.json["links"] == {"self": f"https://127.0.0.1:5000/api/names/{id_}"}


def test_names_search(client_with_login, example_name, headers):
    """Test a successful search."""
    res = client_with_login.get("/names", headers=headers)

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["sortBy"] == "name"
