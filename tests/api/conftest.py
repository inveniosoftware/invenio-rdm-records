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
from invenio_app.factory import create_api
from invenio_pidstore.models import PIDStatus
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2

from invenio_rdm_records.vocabularies import Vocabularies


@pytest.fixture(scope='module')
def create_app(instance_path):
    """Application factory fixture."""
    RecordIdProviderV2.default_status_with_obj = PIDStatus.REGISTERED

    return create_api


@pytest.fixture(scope='function')
def vocabulary_clear(appctx):
    """Clears the Vocabulary singleton and pushes an appctx."""
    Vocabularies.clear()
