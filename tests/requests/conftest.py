# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2021 CERN.
# Copyright (C) 2019-2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from invenio_records_permissions.generators import AuthenticatedUser, SystemProcess

from invenio_rdm_records.services.permissions import RDMRecordPermissionPolicy


class CustomRDMRecordPermissionPolicy(RDMRecordPermissionPolicy):
    """Custom permission policy to enable moderate permission for tests.

    That is needed so users are able to retrieve the `is_verified` field in
    search results.
    """

    can_moderate = [SystemProcess(), AuthenticatedUser()]


@pytest.fixture(scope="module")
def app_config(app_config):
    """Override pytest-invenio app_config fixture."""
    # Allow `is_verified` field to be dumped by anyone for testing user moderation
    app_config["RDM_PERMISSION_POLICY"] = CustomRDMRecordPermissionPolicy
    # Enable user moderation
    app_config["RDM_USER_MODERATION_ENABLED"] = True
    return app_config
