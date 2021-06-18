# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test fixtures for application vocabulary fixtures."""

import pathlib

import pytest
from invenio_access.permissions import system_identity
from invenio_accounts.models import Role
from invenio_app.factory import create_app as _create_app

from invenio_rdm_records.fixtures.vocabularies import VocabulariesFixture


@pytest.fixture()
def vocabularies():
    """Vocabularies object fixture."""
    return VocabulariesFixture(
        system_identity,
        [pathlib.Path(__file__).parent / "data"],
        'vocabularies.yaml',
    )


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
        'invenio_rdm_records.fixtures': [
            'vocabularies_A = mock_module_A.fixtures.vocabularies',
            'vocabularies_B = mock_module_B.fixtures.vocabularies',
        ],
    }


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return _create_app
