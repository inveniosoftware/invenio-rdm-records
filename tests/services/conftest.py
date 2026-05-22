# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-FileCopyrightText: 2020 Northwestern University.
# SPDX-FileCopyrightText: 2021 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from flask_principal import Identity, UserNeed
from invenio_access.permissions import any_user, authenticated_user
from invenio_app.factory import create_api


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return create_api


@pytest.fixture(scope="function")
def anyuser_identity():
    """System identity."""
    identity = Identity(1)
    identity.provides.add(any_user)
    return identity


@pytest.fixture(scope="function")
def authenticated_identity():
    """Authenticated identity fixture."""
    identity = Identity(100)
    identity.provides.add(UserNeed(100))
    identity.provides.add(authenticated_user)
    return identity
