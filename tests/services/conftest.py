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
from invenio_app.factory import create_api
from invenio_pidstore.models import PIDStatus
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2

from invenio_rdm_records.resources import BibliographicDraftActionResource, \
    BibliographicDraftResource, BibliographicRecordResource
from invenio_rdm_records.services import BibliographicRecordService
from invenio_rdm_records.vocabularies import Vocabularies


@pytest.fixture(scope='module')
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


@pytest.fixture(scope='module')
def app(app):
    """app fixture."""
    RecordIdProviderV2.default_status_with_obj = PIDStatus.RESERVED

    record_draft_service = BibliographicRecordService()
    record_bp = BibliographicRecordResource(
        service=record_draft_service
    ).as_blueprint("bibliographic_record_resource")
    draft_bp = BibliographicDraftResource(
        service=record_draft_service
    ).as_blueprint("bibliographic_draft_resource")
    draft_action_bp = BibliographicDraftActionResource(
        service=record_draft_service
    ).as_blueprint("bibliographic_draft_action_resource")

    app.register_blueprint(record_bp)
    app.register_blueprint(draft_bp)
    app.register_blueprint(draft_action_bp)
    return app


@pytest.fixture(scope='function')
def vocabulary_clear(app):
    """Clears the Vocabulary singleton and pushes an application context.

    NOTE: app fixture pushes an application context
    """
    Vocabularies.clear()
