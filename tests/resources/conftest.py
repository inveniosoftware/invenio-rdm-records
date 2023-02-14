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

import pytest
from invenio_app.factory import create_api

from invenio_rdm_records.proxies import current_rdm_records_service


@pytest.fixture(scope="module")
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


@pytest.fixture()
def rdm_record_service():
    """Get the current RDM records service."""
    return current_rdm_records_service


@pytest.fixture()
def community_record(
    uploader, minimal_record, community, rdm_record_service, running_app, db
):
    """Record that belongs to a community."""

    class Record:
        """Test record class."""

        def create_record(self):
            """Creates new record that belongs to the same community."""
            # create draft
            draft = rdm_record_service.create(uploader.identity, minimal_record)
            # Publish
            record = rdm_record_service.publish(uploader.identity, draft.id)
            # TODO replace the following code by the service func that adds the record to a community
            community_record = community._record
            record._record.parent.communities.add(community_record, default=False)
            record._record.parent.commit()
            db.session.commit()
            rdm_record_service.indexer.index(record._record)
            return record

    return Record()


def link(url):
    """Strip the host part of a link."""
    api_prefix = "https://127.0.0.1:5000/api"
    if url.startswith(api_prefix):
        return url[len(api_prefix) :]
