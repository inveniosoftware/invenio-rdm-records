# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Subject resource tests."""

import pytest
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.subjects.api import Subject


@pytest.fixture(scope="module")
def subjects_service():
    return current_service_registry.get("subjects")


@pytest.fixture()
def example_subject(app, db, search_clear, superuser_identity, subjects_service):
    """Example subject."""
    data = {
        "id": "https://id.nlm.nih.gov/mesh/D000001",
        "scheme": "MeSH",
        "subject": "Calcimycin",
    }
    aff = subjects_service.create(superuser_identity, data)
    Subject.index.refresh()  # Refresh the index

    return aff


@pytest.mark.skip(
    "resolving does not work due to url econding. Tried encode/quote, fails."
)
def test_subjects_get(client, example_subject, headers):
    """Test the endpoint to retrieve a single item."""
    id_ = example_subject.id
    res = client.get(f"/subjects/{id_}", headers=headers)
    assert res.status_code == 200
    assert res.json["id"] == id_
    # Test links
    assert res.json["links"] == {
        "self": "https://127.0.0.1:5000/api/subjects/https://id.nlm.nih.gov/mesh/D000001"  # noqa
    }


def test_subjects_search(client, example_subject, headers):
    """Test a successful search."""
    res = client.get("/subjects", headers=headers)

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["sortBy"] == "subject"
