# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test record's communities service."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.proxies import current_record_communities_service
from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.services.errors import MaxNumberCommunitiesExceeded


@pytest.fixture()
def service():
    """Get the current records communities service."""
    return current_record_communities_service


def test_remove_community_from_record_success(
    curator,
    community,
    record_community,
    rdm_record_service,
    service,
):
    """Test removal of a community from a record."""
    data = {"communities": [{"id": community.id}]}
    record = record_community.create_record()
    errors = service.remove(curator.identity, record.pid.pid_value, data)
    assert errors == []

    saved_record = rdm_record_service.read(curator.identity, record.pid.pid_value)
    assert not saved_record.data["parent"]["communities"]


def test_remove_multiple_communities():
    """Test removal of multiple communities of a record."""
    # TODO: implement when the `add` method is implemented
    pass


def test_remove_as_owner(uploader, community, record_community, service):
    """Test that the record's owner can remove the record from a community."""
    data = {"communities": [{"id": community.id}]}
    record = record_community.create_record()

    service.remove(uploader.identity, record.pid.pid_value, data)


def test_remove_as_community_curator(curator, community, record_community, service):
    """Test that the community's curator can remove the record from its community."""
    data = {"communities": [{"id": community.id}]}
    record = record_community.create_record()

    service.remove(curator.identity, record.pid.pid_value, data)


def test_remove_non_existing_community(
    curator,
    record_community,
    rdm_record_service,
    service,
    community,
):
    """Test removal of a non-existing community returns an error."""
    data = {"communities": [{"id": "wrong-id"}]}
    record = record_community.create_record()

    errors = service.remove(curator.identity, record.pid.pid_value, data)
    assert len(errors) == 1

    saved_record = rdm_record_service.read(curator.identity, record.pid.pid_value)
    assert saved_record.data["parent"]["communities"] == {"ids": [str(community.id)]}


def test_remove_existing_and_non_existing_community(
    curator,
    community,
    record_community,
    rdm_record_service,
    service,
):
    """Test removal of existing and non-existing communities."""
    wrong_data = [{"id": "wrong-id"}, {"id": "wrong-id2"}]
    correct_data = [{"id": community.id}]
    data = {"communities": correct_data + wrong_data}
    record = record_community.create_record()

    errors = service.remove(curator.identity, record.pid.pid_value, data)

    assert len(errors) == 2

    saved_record = rdm_record_service.read(curator.identity, record.pid.pid_value)
    assert not saved_record.data["parent"]["communities"]


def test_remove_missing_permission(test_user, community, record_community, service):
    """Test that a random user cannot remove the record from a community."""
    data = {"communities": [{"id": community.id}]}
    record = record_community.create_record()

    errors = service.remove(test_user.identity, record.pid.pid_value, data)

    assert len(errors) == 1
    assert errors[0]["community"] == community.id
    assert errors[0]["message"] == "Permission denied."


def test_remove_another_community(
    db,
    curator,
    community2,
    record_community,
    service,
    rdm_record_service,
):
    """Test error when removing a community by a curator of another community."""

    # TODO: remove this extra func when the `add` to a community is implemented
    def add_to_community2(record):
        record.parent.communities.add(community2._record, default=False)
        record.parent.commit()
        record.commit()
        db.session.commit()
        rdm_record_service.indexer.index(record)
        RDMRecord.index.refresh()
        return record

    record = record_community.create_record()
    record = add_to_community2(record)
    # record is part of `community` and `community2`
    # curator is curator of `community`: it cannot remove it from `community2`

    data = {"communities": [{"id": community2.id}]}
    errors = service.remove(curator.identity, record.pid.pid_value, data)

    assert len(errors) == 1
    assert errors[0]["community"] == community2.id
    assert errors[0]["message"] == "Permission denied."


def test_remove_too_many_communities(curator, record_community, service):
    """Test that passing too many communities throws an error."""
    random_community = {"id": "random-id"}
    record = record_community.create_record()

    lots_of_communities = []
    while len(lots_of_communities) <= service.config.max_number_of_removals:
        lots_of_communities.append(random_community)
    data = {"communities": lots_of_communities}
    with pytest.raises(MaxNumberCommunitiesExceeded):
        service.remove(curator.identity, record.pid.pid_value, data)


def test_remove_empty_communities(curator, record_community, service):
    """Test removal of communities from record with empty payload."""
    data = {"communities": []}
    record = record_community.create_record()

    with pytest.raises(ValidationError):
        service.remove(curator.identity, record.pid.pid_value, data)
