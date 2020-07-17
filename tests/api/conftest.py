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

from datetime import datetime

import pytest
from invenio_app.factory import create_api
from invenio_records_resources.resource_units import IdentifiedRecord

from invenio_rdm_records.resources import BibliographicRecordResource
from invenio_rdm_records.services import BibliographicRecordService
from invenio_rdm_records.vocabularies import Vocabularies


@pytest.fixture(scope='module')
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


@pytest.fixture(scope='function')
def vocabulary_clear(appctx):
    """Clears the Vocabulary singleton and pushes an appctx."""
    Vocabularies.clear()


class FakeBibliographicRecordService(BibliographicRecordService):
    """Fake Bibliogrpahic Record Service.

    Mocks out the search() method.

    TODO: Remove me when integration / implementation complete.
    """

    class FakeRecord:
        """Fake Record for mocking purposes."""

        def __init__(self, revision_id):
            """Constructor."""
            self.revision_id = revision_id
            self.created = datetime.now()
            self.updated = datetime.now()

        def dumps(self):
            """Dump record."""
            return {
                "access_right": "open",
                "resource_type": {
                    "type": "image",
                    "subtype": "image-photo"
                },
                "creators": [],
                "titles": [{
                    "title": "A Romans story",
                    "type": "Other",
                    "lang": "eng"
                }]
            }

    class FakePID:
        """Fake PID for mocking purposes."""

        def __init__(self, pid_value):
            """Constructor."""
            self.pid_value = pid_value

    def search(self, querystring, identity, pagination=None, *args, **kwargs):
        """Mocked Search."""
        records = [
            IdentifiedRecord(
                record=self.FakeRecord(1), pid=self.FakePID('fake-id-1')
            ),
            IdentifiedRecord(
                record=self.FakeRecord(2), pid=self.FakePID('fake-id-2')
            ),
        ]
        total = 2
        aggregations = {}

        return self.resource_list(records, total, aggregations)


@pytest.fixture(scope='module')
def app(app):
    """app fixture."""
    # TODO: Take out Mocks when endpoints actually implemented
    resource = BibliographicRecordResource(
        service=FakeBibliographicRecordService()
    )
    bp = resource.as_blueprint("bibliographic_resource")
    app.register_blueprint(bp)
    return app
