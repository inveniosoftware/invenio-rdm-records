# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

from copy import deepcopy

import pytest
from invenio_app.factory import create_api

from invenio_rdm_records import config


@pytest.fixture(scope='module')
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


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


@pytest.fixture()
def headers():
    """Default headers for making requests."""
    return {
        'content-type': 'application/json',
        'accept': 'application/json',
    }


@pytest.fixture(scope='function')
def full_record_ui(full_record):
    """Full record dereferenced data, as is expeceted by the UI serializer."""
    ui_record = deepcopy(full_record)
    ui_record["metadata"]["creators"] = [{
        "name": "Nielsen, Lars Holm",
        "type": "personal",
        "given_name": "Lars Holm",
        "family_name": "Nielsen",
        "identifiers": {
            "orcid": "0000-0001-8135-3489"
        },
        "affiliations": [{
            "name": "CERN",
            "identifiers": {
                "ror": "01ggx4157",
                "isni": "000000012156142X"
            }
        }]
    }]

    ui_record["metadata"]["contributors"] = [{
        "name": "Nielsen, Lars Holm",
        "type": "personal",
        "role": "other",
        "given_name": "Lars Holm",
        "family_name": "Nielsen",
        "identifiers": {
            "orcid": "0000-0001-8135-3489"
        },
        "affiliations": [{
            "name": "CERN",
            "identifiers": {
                "ror": "01ggx4157",
                "isni": "000000012156142X"
            }
        }]
    }]

    ui_record["metadata"]["languages"] = [{
        "id": "da",
        "title": {"en": "Danish"}
    }, {
        "id": "en",
        "title": {"en": "English"}
    }]

    return ui_record
