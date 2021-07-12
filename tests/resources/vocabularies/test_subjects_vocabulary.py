# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Subject resource tests."""

from urllib.parse import quote

import pytest
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.subjects.api import Subject


@pytest.fixture(scope="module")
def subjects_service():
    return current_service_registry.get("rdm-subjects")


@pytest.fixture()
def example_subject(
    app, db, es_clear, superuser_identity, subjects_service
):
    """Example subject."""
    data = {
        "id": "https://id.nlm.nih.gov/mesh/D000001",
        "scheme": "MeSH",
        "subject": "Calcimycin",
    }
    aff = subjects_service.create(superuser_identity, data)
    Subject.index.refresh()  # Refresh the index

    return aff


def test_subjects_get(client, example_subject, headers):
    """Test the endpoint to retrieve a single item."""
    id_ = example_subject.id
    res = client.get(f"/subjects/{id_}", headers=headers)
    assert res.status_code == 200
    assert res.json["id"] == id_
    # test encoding the URL ID too
    res = client.get(f"/subjects/{quote(id_)}", headers=headers)
    assert res.status_code == 200
    # Test links
    assert res.json["links"] == {
        "self": "https://127.0.0.1:5000/api/subjects/https%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2FD000001"  # noqa
    }


def test_subjects_search(client, example_subject, headers):
    """Test a successful search."""
    res = client.get("/subjects", headers=headers)

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["sortBy"] == "subject"
