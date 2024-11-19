# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test community records service."""

from copy import deepcopy

import pytest
from invenio_records_resources.services.errors import PermissionDeniedError
from marshmallow import ValidationError

from invenio_rdm_records.collections.api import Collection, CollectionTree
from invenio_rdm_records.proxies import (
    current_community_records_service,
    current_rdm_records_service,
)
from invenio_rdm_records.records import RDMRecord


@pytest.fixture()
def service():
    """Get the current community records service."""
    return current_community_records_service


def test_remove_record_from_community_success(
    curator, community, record_community, service
):
    """Test removal of a record from a community."""
    record = record_community.create_record()
    data = {"records": [{"id": record.pid.pid_value}]}
    errors = service.delete(curator.identity, str(community.id), data)

    assert errors == []


def test_remove_records_from_community_success(
    curator, community, record_community, service
):
    """Test removal of a multiple records from a community."""
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
    errors = service.delete(curator.identity, str(community.id), data)

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


def test_remove_non_existing_record(curator, community, service):
    """Test error on removing a non-existing record from a community."""
    data = {"records": [{"id": "wrong-id"}]}
    errors = service.delete(curator.identity, str(community.id), data)

    assert len(errors) == 1
    assert errors[0]["message"] == "The record does not exist."


def test_remove_record_of_other_community(
    db, curator, community, community2, record_community, service
):
    """Test error on removing a record that belongs to another community."""

    def add_to_community2(record):
        record.parent.communities.remove(community._record)
        record.parent.communities.add(community2._record, default=False)
        record.parent.commit()
        record.commit()
        db.session.commit()
        current_rdm_records_service.indexer.index(record)
        RDMRecord.index.refresh()
        return record

    record_comm2 = record_community.create_record()
    record_comm2 = add_to_community2(record_comm2)

    data = {"records": [{"id": record_comm2.pid.pid_value}]}
    errors = service.delete(curator.identity, str(community.id), data)

    assert len(errors) == 1
    assert "not included in the community" in errors[0]["message"]


def test_remove_records_from_communities_success_w_errors(
    curator, community, record_community, service
):
    """Test removal of records from communities with errors."""
    record = record_community.create_record()
    correct_data = [{"id": record.pid.pid_value}]
    wrong_data = [{"id": "wrong-id"}, {"id": "wrong-id2"}]
    data = {"records": correct_data + wrong_data}
    errors = service.delete(curator.identity, str(community.id), data)

    assert len(errors) == 2


def test_remove_too_many_records(curator, community, record_community, service):
    """Test removal of too many records from a community."""
    random_record = {"id": "random-id"}
    lots_of_records = []
    while len(lots_of_records) <= service.config.max_number_of_removals:
        lots_of_records.append(random_record)
    data = {"records": lots_of_records}
    with pytest.raises(ValidationError):
        service.delete(curator.identity, str(community.id), data)


def test_remove_w_empty_payload(curator, community, service):
    """Test removal of records from communities with empty payload."""
    data = {"records": []}
    with pytest.raises(ValidationError):
        service.delete(curator.identity, str(community.id), data)


def test_search_community_records(
    community, record_community, service, anyuser_identity, uploader
):
    """Test search for records in a community."""
    results = service.search(
        anyuser_identity,
        community_id=str(community.id),
    )
    assert results.to_dict()["hits"]["total"] == 0

    record_community.create_record()
    record_community.create_record()
    record_community.create_record()

    for identity in [anyuser_identity, uploader.identity]:
        results = service.search(
            identity,
            community_id=str(community.id),
        )
        assert results.to_dict()["hits"]["total"] == 3
