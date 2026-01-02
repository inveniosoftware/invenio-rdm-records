# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""CodeMeta specific test configs."""

import pytest
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary

from invenio_rdm_records.cli import (
    create_records_custom_field,
    custom_field_exists_in_records,
)
from invenio_rdm_records.contrib.codemeta.custom_fields import (
    CODEMETA_CUSTOM_FIELDS,
    CODEMETA_FACETS,
    CODEMETA_NAMESPACE,
)
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records.api import RDMDraft, RDMRecord


@pytest.fixture(scope="module")
def custom_field_exists(cli_runner):
    """Factory fixture, tests whether a given custom field exists."""

    def _custom_field_exists(cf_name):
        return cli_runner(custom_field_exists_in_records, "-f", cf_name)

    return _custom_field_exists


@pytest.fixture(scope="function")
def initialise_custom_fields(app, location, db, search_clear, cli_runner):
    """Fixture initialises custom fields."""
    return cli_runner(create_records_custom_field)


@pytest.fixture(scope="function")
def initialise_codemeta_custom_fields(
    cli_runner, app_codemeta_config, search_clear, db, location, running_app
):
    """Initialised codemeta custom fields."""
    app = running_app.app
    original_config = app.config.copy()
    app.config = {**app.config, **app_codemeta_config}
    yield cli_runner(create_records_custom_field)
    app.config = original_config


@pytest.fixture(scope="session")
def app_codemeta_config(
    codemeta_cf_facetted_term,
):
    """Yields the app config fixture with codemeta CF specific configs injected."""
    code_meta_configs = {
        "RDM_CUSTOM_FIELDS": CODEMETA_CUSTOM_FIELDS,
        "RDM_NAMESPACES": CODEMETA_NAMESPACE,
        "RDM_FACETS": CODEMETA_FACETS,
        "RDM_SEARCH": {
            "facets": [codemeta_cf_facetted_term],
        },
    }
    return code_meta_configs


@pytest.fixture(scope="module")
def service():
    """Rdm records service instance."""
    return current_rdm_records_service


@pytest.fixture(scope="function")
def codemeta_development_status(running_app):
    """Creates and retrieves a vocabulary type."""
    v = vocabulary_service.create_type(system_identity, "code:developmentStatus", "ds")
    return v


@pytest.fixture(scope="session")
def codemeta_development_status_vocabulary_data():
    """Fixture returns 'codemeta:developmentStatus' vocabulary data."""
    return {
        "id": "concept",
        "title": {
            "en": "Concept",
        },
        "description": {
            "en": "Minimal or no implementation has been done yet, or the repository is only intended to be a limited example, demo, or proof-of-concept."
        },
        "type": "code:developmentStatus",
    }


@pytest.fixture(scope="function")
def codemeta_development_status_vocabulary(
    codemeta_development_status,
    codemeta_development_status_vocabulary_data,
):
    """Creates and retrieves controlled vocabulary 'development status'."""
    record = vocabulary_service.create(
        identity=system_identity,
        data=codemeta_development_status_vocabulary_data,
    )
    Vocabulary.index.refresh()  # Refresh the index

    return record


@pytest.fixture(scope="session")
def codemeta_cf_name():
    """Example of a codemeta custom field name."""
    return "code:developmentStatus"


@pytest.fixture(scope="session")
def codemeta_cf_value():
    """Example of a codemeta custom field value (from controlled vocabulary)."""
    return "concept"


@pytest.fixture(scope="session")
def codemeta_cf_facetted_term():
    """Example of a codemeta custom field term that is used as a facet term."""
    return "developmentStatus"


@pytest.fixture(scope="function")
def minimal_codemeta_record(minimal_record, codemeta_cf_name, codemeta_cf_value):
    """Represents a record containing codemeta fields (custom fields)."""
    return {
        **minimal_record,
        "custom_fields": {codemeta_cf_name: {"id": codemeta_cf_value}},
    }


@pytest.fixture(scope="function")
def codemeta_record(
    codemeta_development_status_vocabulary,
    db,
    minimal_codemeta_record,
    service,
    search_clear,
    superuser_identity,
):
    """Creates a record with codemeta custom fields added.

    The record is teared down with the db fixture, when the session is destroyed.
    Record's indexed document is deleted by the fixture "search_clear".
    """
    draft = service.create(superuser_identity, minimal_codemeta_record)
    record = service.publish(id_=draft.id, identity=superuser_identity)
    RDMRecord.index.refresh()
    return record
    # Search teardown is taken care by 'search_clear' fixture
    # DB teardown is taken care by 'db' fixture
