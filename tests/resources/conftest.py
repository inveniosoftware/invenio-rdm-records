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

from collections import namedtuple
from copy import deepcopy

import pytest
from invenio_access.permissions import system_identity
from invenio_app.factory import create_api
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary

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


@pytest.fixture(scope="module")
def laguanges_v(app, languages_type):
    """Language vocabulary records."""
    lang = []

    lang.append(vocabulary_service.create(system_identity, {
        "id": "eng",
        "title": {
            "en": "English",
            "da": "Engelsk",
        },
        "props": {"alpha_2": "en"},
        "tags": ["individual", "living"],
        "type": "languages"
    }))

    lang.append(vocabulary_service.create(system_identity, {
        "id": "dan",
        "title": {
            "en": "Danish",
            "da": "Dansk",
        },
        "props": {"alpha_2": "da"},
        "tags": ["individual", "living"],
        "type": "languages"
    }))

    Vocabulary.index.refresh()

    return lang


@pytest.fixture(scope="function")
def resource_type_type(app):
    """Resource type vocabulary type."""
    return vocabulary_service.create_type(
        system_identity, "resource_types", "rsrct")


@pytest.fixture(scope="function")
def resource_type_v(app, resource_type_type):
    """Resource type vocabulary record."""
    vocabulary_service.create(system_identity, {  # create base resource type
        "id": "image",
        "props": {
            "csl": "figure",
            "datacite_general": "Image",
            "datacite_type": "",
            "openaire_resourceType": "25",
            "openaire_type": "dataset",
            "schema.org": "https://schema.org/ImageObject",
            "subtype": "",
            "subtype_name": "",
            "type": "image",
            "type_icon": "chart bar outline",
            "type_name": "Image",
        },
        "title": {
            "en": "Image"
        },
        "type": "resource_types"
    })

    vocab = vocabulary_service.create(system_identity, {
        "id": "image-photo",
        "props": {
            "csl": "graphic",
            "datacite_general": "Image",
            "datacite_type": "Photo",
            "openaire_resourceType": "25",
            "openaire_type": "dataset",
            "schema.org": "https://schema.org/Photograph",
            "subtype": "image-photo",
            "subtype_name": "Photo",
            "type": "image",
            "type_icon": "chart bar outline",
            "type_name": "Image",
        },
        "title": {
            "en": "Photo"
        },
        "type": "resource_types"
    })

    Vocabulary.index.refresh()

    return vocab


RunningApp = namedtuple("RunningApp", [
    "app", "location", "resource_type_v"
])


@pytest.fixture
def running_app(app, location, resource_type_v):
    """This fixture provides an app with the typically needed db data loaded.

    All of these fixtures are often needed together, so collecting them
    under a semantic umbrella makes sense.
    """
    return RunningApp(app, location, resource_type_v)
