# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test community records service."""

import pytest
from invenio_records_resources.services.errors import PermissionDeniedError
from marshmallow import ValidationError

from invenio_rdm_records.proxies import (
    current_community_records_service,
    current_rdm_records_service,
)
from invenio_rdm_records.records import RDMDraft, RDMRecord
from invenio_rdm_records.services.errors import MaxNumberOfRecordsExceed


@pytest.fixture()
def service():
    """Get the current community records service."""
    return current_community_records_service


def test_remove_record_from_community_success(
    running_app, community, record_community, service
):
    """Test removal of a record from a community."""
    superuser_identity = running_app.superuser_identity
    record = record_community.create_record()
    data = {"records": [{"id": record.pid.pid_value}]}
    errors = service.delete(superuser_identity, str(community.id), data)

    assert errors == []


def test_remove_records_from_community_success(
    running_app, community, record_community, service
):
    """Test removal of a multiple records from a community."""
    superuser_identity = running_app.superuser_identity
    record1 = record_community.create_record()
    record2 = record_community.create_record()
    record3 = record_community.create_record()
    data = {
        "records": [
            {"id": record1.pid.pid_value},
            {"id": record2.pid.pid_value},
            {"id": record3.pid.pid_value},
        ]
    }
    errors = service.delete(superuser_identity, str(community.id), data)

    assert errors == []


def test_missing_permission(test_user, community, record_community, service):
    """Test missing permissions to delete."""
    record = record_community.create_record()
    data = {"records": [{"id": record.pid.pid_value}]}
    with pytest.raises(PermissionDeniedError):
        service.delete(test_user.identity, str(community.id), data)


def test_curator_permission(curator, community, record_community, service):
    """Test curator permissions to delete."""
    record = record_community.create_record()
    data = {"records": [{"id": record.pid.pid_value}]}
    errors = service.delete(curator.identity, str(community.id), data)

    assert errors == []


def test_remove_record_from_community_error(running_app, community, service):
    """Test error on removing a wrong record from a community."""
    superuser_identity = running_app.superuser_identity
    data = {"records": [{"id": "wrong-id"}]}
    errors = service.delete(superuser_identity, str(community.id), data)

    assert len(errors) == 1


def test_remove_records_from_communities_success_w_errors(
    running_app, community, record_community, service
):
    """Test removal of records from communities with errors."""
    superuser_identity = running_app.superuser_identity
    record = record_community.create_record()
    correct_data = [{"id": record.pid.pid_value}]
    wrong_data = [{"id": "wrong-id"}, {"id": "wrong-id2"}]
    data = {"records": correct_data + wrong_data}
    errors = service.delete(superuser_identity, str(community.id), data)

    assert len(errors) == 2


def test_remove_too_many_records(running_app, community, record_community, service):
    """Test removal of too many records from a community."""
    superuser_identity = running_app.superuser_identity
    random_record = {"id": "random-id"}
    lots_of_records = []
    while len(lots_of_records) <= service.config.max_number_of_removals:
        lots_of_records.append(random_record)
    data = {"records": lots_of_records}
    with pytest.raises(MaxNumberOfRecordsExceed):
        service.delete(superuser_identity, str(community.id), data)


def test_remove_w_empty_payload(running_app, community, service):
    """Test removal of records from communities with empty payload."""
    superuser_identity = running_app.superuser_identity
    data = {"records": []}
    with pytest.raises(ValidationError):
        service.delete(superuser_identity, str(community.id), data)


def test_search_community_records(
    db, running_app, minimal_record, community, anyuser_identity
):
    """Test search for records in a community."""
    service = current_rdm_records_service
    community_records = current_community_records_service
    community = community._record

    def _create_record():
        """Create a record."""
        # create draft
        draft = RDMDraft.create(minimal_record)
        draft.commit()
        db.session.commit()
        # publish and get record
        record = RDMRecord.publish(draft)
        record.commit()
        db.session.commit()
        return record

    def _add_to_community(record, community, default):
        """Add record to community."""
        record.parent.communities.add(community, default=default)
        record.parent.commit()
        record.commit()
        db.session.commit()
        service.indexer.index(record)
        RDMRecord.index.refresh()

    # ensure that there no records in the community
    results = community_records.search(
        anyuser_identity,
        community_id=community.id,
    )
    assert results.to_dict()["hits"]["total"] == 0

    # add record to community, with default false
    record1 = _create_record()
    _add_to_community(record1, community, False)

    # ensure that the record is in the community
    results = community_records.search(
        anyuser_identity,
        community_id=community.id,
    )
    assert results.to_dict()["hits"]["total"] == 1

    # add another record to community, with default true
    record2 = _create_record()
    _add_to_community(record2, community, True)

    # ensure that the record is in the community
    results = community_records.search(
        anyuser_identity,
        community_id=community.id,
    )
    assert results.to_dict()["hits"]["total"] == 2

    # ensure that searching by community slug also works
    results = community_records.search(
        anyuser_identity,
        community_id=community.slug,
    )
    assert results.to_dict()["hits"]["total"] == 2
