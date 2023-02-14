# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from flask_principal import Identity, UserNeed
from invenio_access.permissions import any_user, authenticated_user
from invenio_app.factory import create_api

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.records import RDMRecord


@pytest.fixture(scope="module")
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


@pytest.fixture(scope="function")
def anyuser_identity():
    """System identity."""
    identity = Identity(1)
    identity.provides.add(any_user)
    return identity


@pytest.fixture(scope="function")
def authenticated_identity():
    """Authenticated identity fixture."""
    identity = Identity(1)
    identity.provides.add(UserNeed(1))
    identity.provides.add(authenticated_user)
    return identity


@pytest.fixture()
def rdm_record_service():
    """Get the current RDM records service."""
    return current_rdm_records_service


@pytest.fixture()
def record_community(db, uploader, minimal_record, community, rdm_record_service):
    """Creates a record that belongs to a community."""

    class Record:
        """Test record class."""

        def create_record(self):
            """Creates new record that belongs to the same community."""
            # create draft
            community_record = community._record
            draft = rdm_record_service.create(uploader.identity, minimal_record)
            # publish and get record
            record = RDMRecord.publish(draft._record)
            record.commit()
            record.parent.communities.add(community_record, default=False)
            record.parent.commit()
            record.commit()
            # Manually register the pid to be able to resolve it
            record.pid.register()
            db.session.commit()
            rdm_record_service.indexer.index(record)
            RDMRecord.index.refresh()
            return record

    return Record()
