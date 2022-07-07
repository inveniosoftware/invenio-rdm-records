# -*- coding: utf-8 -*-
#
# Copyright (C) 202 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.awards.api import Award
from invenio_vocabularies.contrib.funders.api import Funder


@pytest.fixture(scope="module")
def funders_service(app):
    """Funders service."""
    return current_service_registry.get("funders")


@pytest.fixture()
def example_funder(app, db, search_clear, superuser_identity, funders_service):
    """Example funder."""
    data = {
        "id": "01ggx4157",
        "identifiers": [{"identifier": "01ggx4157", "scheme": "ror"}],
        "name": "CERN",
        "title": {
            "en": "European Organization for Nuclear Research",
        },
        "country": "CH",
    }
    fun = funders_service.create(superuser_identity, data)
    Funder.index.refresh()  # Refresh the index

    yield fun

    funders_service.delete(superuser_identity, fun.id)


@pytest.fixture(scope="module")
def awards_service(app):
    """Awards service."""
    return current_service_registry.get("awards")


@pytest.fixture()
def example_award(
    app,
    db,
    search_clear,
    superuser_identity,
    awards_service,
    example_funder,
):
    """Example award."""
    data = {
        "id": "755021",
        "identifiers": [
            {
                "identifier": "https://cordis.europa.eu/project/id/755021",
                "scheme": "url",
            }
        ],
        "number": "755021",
        "title": {
            "en": "Personalised Treatment For Cystic Fibrosis Patients With \
                Ultra-rare CFTR Mutations (and beyond)",
        },
        "funder": {"id": "01ggx4157"},
    }
    awa = awards_service.create(superuser_identity, data)
    Award.index.refresh()  # Refresh the index

    yield awa

    awards_service.delete(superuser_identity, awa.id)
