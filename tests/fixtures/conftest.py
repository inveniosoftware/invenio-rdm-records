# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test fixtures for application vocabulary fixtures."""

from pathlib import Path

import pytest
from invenio_access.permissions import system_identity
from invenio_accounts.models import Role
from invenio_app.factory import create_app as _create_app
from invenio_vocabularies.contrib.awards.api import Award
from invenio_vocabularies.contrib.funders.api import Funder
from invenio_vocabularies.records.api import Vocabulary

from invenio_rdm_records.fixtures.vocabularies import VocabulariesFixture


@pytest.fixture(scope="function")
def admin_role(db):
    """Create an admin role."""
    role = Role(name="admin")
    db.session.add(role)
    db.session.commit()
    return role


@pytest.fixture(scope="module")
def extra_entry_points():
    """Vocabularies entry points."""
    return {
        "invenio_rdm_records.fixtures": [
            "vocabularies_A = tests.fixtures.mock_module_A.fixtures.vocabularies",
            "vocabularies_B = tests.fixtures.mock_module_B.fixtures.vocabularies",
        ],
        "invenio_base.blueprints": [
            "invenio_app_rdm_records = tests.mock_module:create_invenio_app_rdm_records_blueprint",  # noqa
            "invenio_app_rdm_requests = tests.mock_module:create_invenio_app_rdm_requests_blueprint",  # noqa
            "invenio_app_rdm_communities = tests.mock_module:create_invenio_app_rdm_communities_blueprint",  # noqa
        ],
    }


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return _create_app


@pytest.fixture
def vocabularies():
    """Load vocabularies."""
    vocabularies = VocabulariesFixture(
        system_identity,
        Path(__file__).parent / "data/vocabularies.yaml",
        delay=False,
    )
    vocabularies.load()
    Vocabulary.index.refresh()
    Award.index.refresh()
    Funder.index.refresh()
