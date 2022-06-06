# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from flask_principal import Identity, UserNeed
from invenio_access.permissions import any_user, authenticated_user
from invenio_app.factory import create_api


@pytest.fixture(scope="module")
def create_app(instance_path):
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
    identity = Identity(1)
    identity.provides.add(UserNeed(1))
    identity.provides.add(authenticated_user)
    return identity
