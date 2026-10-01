# SPDX-FileCopyrightText: TU Wien.
# SPDX-License-Identifier: MIT

"""Configuration for storage service tests."""

import pytest


@pytest.fixture(scope="module")
def app_config(app_config):
    """Set quota size for storage service."""
    app_config["RDM_FILES_DEFAULT_MAX_ADDITIONAL_QUOTA_SIZE"] = 20 * 10**9
    app_config["RDM_FILES_DEFAULT_QUOTA_SIZE"] = 10 * 10**9
    return app_config
