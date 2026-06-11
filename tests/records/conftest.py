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
from invenio_app.factory import create_api
from invenio_indexer.api import RecordIndexer

from invenio_rdm_records.records.api import RDMDraft


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    return {
        "invenio_administration.views": [
            "invenio_app_rdm_records_list = tests.mock_module.administration:RecordAdminListView",
            "invenio_app_rdm_drafts_list = tests.mock_module.administration:DraftAdminListView",
            "invenio_requests_user_moderation_list = tests.mock_module.administration:UserModerationListView",
        ],
        "invenio_base.blueprints": [
            "invenio_app_rdm_records = tests.mock_module:create_invenio_app_rdm_records_blueprint",  # noqa
            "invenio_app_rdm_requests = tests.mock_module:create_invenio_app_rdm_requests_blueprint",  # noqa
            "invenio_app_rdm_communities = tests.mock_module:create_invenio_app_rdm_communities_blueprint",  # noqa
        ],
        "invenio_db.model": [
            "mock_module = tests.records.mock_module.models",
        ],
        "invenio_jsonschemas.schemas": [
            "mock_module = tests.records.mock_module.jsonschemas",
        ],
        "invenio_search.mappings": [
            "mocks = tests.records.mock_module.mappings",
        ],
    }


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return create_api


@pytest.fixture()
def indexer():
    """Indexer instance with correct Record class."""
    return RecordIndexer(
        record_cls=RDMDraft, record_to_index=lambda r: (r.index._name, "_doc")
    )
