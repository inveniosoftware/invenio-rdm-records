# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
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
from invenio_rdm_records.vocabularies import Vocabularies


@pytest.fixture(scope='module')
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


@pytest.fixture(scope='function')
def vocabulary_clear(appctx):
    """Clears the Vocabulary singleton and pushes an appctx."""
    Vocabularies.clear()


@pytest.fixture()
def indexer():
    """Indexer instance with correct Record class."""
    return RecordIndexer(
        record_cls=RDMDraft, record_to_index=lambda r: (r.index._name, '_doc')
    )
