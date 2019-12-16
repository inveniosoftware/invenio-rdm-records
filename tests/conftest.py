# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modifya
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from invenio_app.factory import create_app as _create_app

from invenio_rdm_records import config


@pytest.fixture(scope='module')
def celery_config():
    """Override pytest-invenio fixture."""
    return {}


@pytest.fixture(scope='module')
def app_config(app_config):
    """Override pytest-invenio app_config fixture.

    For test purposes we need to enforce the configuration variables set in
    config.py. Because invenio-rdm-records is not a flavour extension, it does
    not enforce them via a config entrypoint or ext.py; only flavour
    extensions are allowed to forcefully set configuration.

    This means there is a clash between configuration set by
    invenio-records-rest and this module for instance. We want this module's
    config.py to apply in tests.
    """
    supported_configurations = [
        'FILES_REST_PERMISSION_FACTORY',
        'PIDSTORE_RECID_FIELD',
        'RECORDS_REST_ENDPOINTS',
        'RECORDS_REST_FACETS',
        'RECORDS_REST_SORT_OPTIONS',
        'RECORDS_REST_DEFAULT_SORT',
        'RECORDS_FILES_REST_ENDPOINTS',
        'RECORDS_PERMISSIONS_RECORD_POLICY'
    ]

    for config_key in supported_configurations:
        app_config[config_key] = getattr(config, config_key, None)

    return app_config


@pytest.fixture(scope='module')
def create_app():
    """Create app fixture for UI+API app."""
    return _create_app
