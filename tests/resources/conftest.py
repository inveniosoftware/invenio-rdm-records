# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from flask_principal import Identity, Need, UserNeed
from invenio_app.factory import create_api

from invenio_rdm_records import config
from invenio_rdm_records.resources import BibliographicDraftActionResource, \
    BibliographicDraftActionResourceConfig, BibliographicDraftResource, \
    BibliographicDraftResourceConfig, BibliographicRecordResource, \
    BibliographicRecordResourceConfig
from invenio_rdm_records.services import BibliographicRecordService, \
    BibliographicRecordServiceConfig


@pytest.fixture(scope='module')
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


@pytest.fixture(scope="module")
def record_resource():
    """Resource."""
    return BibliographicRecordResource(
        config=BibliographicRecordResourceConfig(),
        service=BibliographicRecordService(
            config=BibliographicRecordServiceConfig()
        )
    )


@pytest.fixture(scope="module")
def draft_resource():
    """Resource."""
    return BibliographicDraftResource(
        config=BibliographicDraftResourceConfig(),
        service=BibliographicRecordService(
            config=BibliographicRecordServiceConfig()
        )
    )


@pytest.fixture(scope="module")
def action_resource():
    """Action Resource."""
    return BibliographicDraftActionResource(
        config=BibliographicDraftActionResourceConfig(),
        service=BibliographicRecordService(
            config=BibliographicRecordServiceConfig()
        )
    )


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
    ]

    for config_key in supported_configurations:
        app_config[config_key] = getattr(config, config_key, None)

    # Temporarly force to delete records rest default endpoints until
    # we completely remove the dependency on the module
    app_config["RECORDS_REST_ENDPOINTS"] = {}

    return app_config


@pytest.fixture(scope="module")
def base_app(base_app, record_resource, draft_resource, action_resource):
    """Application factory fixture."""
    base_app.register_blueprint(
        record_resource.as_blueprint('record_resource'))
    base_app.register_blueprint(draft_resource.as_blueprint('draft_resource'))
    base_app.register_blueprint(action_resource.as_blueprint('draft_action'))
    yield base_app


@pytest.fixture(scope="module")
def identity_simple():
    """Simple identity fixture."""
    i = Identity(1)
    i.provides.add(UserNeed(1))
    i.provides.add(Need(method='system_role', value='any_user'))
    return i
