# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test record's communities service."""

import pytest
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests import current_requests_service
from marshmallow import ValidationError

from invenio_rdm_records.proxies import (
    current_community_records_service,
    current_record_communities_service,
)
from invenio_rdm_records.requests.community_inclusion import CommunityInclusion
from invenio_rdm_records.services.errors import MaxNumberCommunitiesExceeded


@pytest.fixture()
def service():
    """Get the current records communities service."""
    return current_record_communities_service


@pytest.fixture()
def requests_service():
    """Get the current RDM requests service."""
    return current_requests_service


@pytest.fixture()
def community_records_service():
    """Get the current community records service."""
    return current_community_records_service


def add_to_community(db, rdm_record_service, record, community):
    record.parent.communities.add(community._record, default=False)
    record.parent.commit()
    record.commit()
    db.session.commit()
    rdm_record_service.indexer.index(record, arguments={"refresh": True})
    return record


def test_uploader_add_record_to_communities(
    uploader,
    community,
    open_review_community,
    closed_review_community,
    record_community,
    service,
    rdm_record_service,
    requests_service,
    anyuser_identity,
    community_records_service,
):
    """Test uploader addition of record to open review and closed review community."""
    data = {
        "communities": [
            {"id": open_review_community.id},
            {"id": closed_review_community.id},
        ]
    }
    record = record_community.create_record()

    results = service.add(uploader.identity, record.pid.pid_value, data)
    assert not results["errors"]
    assert len(results["success"]) == 2

    record_item = rdm_record_service.read(uploader.identity, record.pid.pid_value)
    record_communities = record_item.data["parent"]["communities"]["ids"]
    # assert that no communities have been added yet
    assert len(record_communities) == 1
    assert community.id in record_communities
    assert open_review_community.id not in record_communities
    assert closed_review_community.id not in record_communities

    # assert that requests are "submitted", but not "accepted"
    for result in results["success"]:
        request_id = result["request"]
        request = requests_service.read(uploader.identity, request_id).to_dict()
        assert request["status"] == "submitted"
        assert request["type"] == CommunityInclusion.type_id
        assert request["is_open"] is True

    # check search results
    for community_id, expected_n_results in [
        (community.id, 1),
        (open_review_community.id, 0),
        (closed_review_community.id, 0),
    ]:
        results = community_records_service.search(
            anyuser_identity,
            community_id=str(community_id),
        )
        assert results.to_dict()["hits"]["total"] == expected_n_results


def test_community_owner_add_record_to_communities(
    curator,
    inviter,
    community,
    open_review_community,
    closed_review_community,
    record_community,
    service,
    rdm_record_service,
    requests_service,
    anyuser_identity,
    community_records_service,
):
    """Test owner addition of record to open review and closed review community."""
    data = {
        "communities": [
            {"id": open_review_community.id},
            {"id": closed_review_community.id},
        ]
    }
    inviter(curator.id, open_review_community.id, "curator")
    inviter(curator.id, closed_review_community.id, "curator")
    record = record_community.create_record(uploader=curator)

    results = service.add(curator.identity, record.pid.pid_value, data)
    assert not results["errors"]
    assert len(results["success"]) == 2

    record_item = rdm_record_service.read(curator.identity, record.pid.pid_value)
    record_communities = record_item.data["parent"]["communities"]["ids"]
    # assert that only the curator's community has been added
    assert len(record_communities) == 2
    assert community.id in record_communities
    assert open_review_community.id in record_communities
    assert closed_review_community.id not in record_communities

    # assert that the request of the curator is "accepted"
    for result in results["success"]:
        community_id = result["community"]
        request_id = result["request"]
        request = requests_service.read(curator.identity, request_id).to_dict()
        assert request["type"] == CommunityInclusion.type_id
        if community_id == open_review_community.id:
            assert request["status"] == "accepted"
            assert request["is_open"] is False
        elif community_id == closed_review_community.id:
            assert request["status"] == "submitted"
            assert request["is_open"] is True
        else:
            raise

    # check search results
    for community_id, expected_n_results in [
        (community.id, 1),
        (open_review_community.id, 1),
        (closed_review_community.id, 0),
    ]:
        results = community_records_service.search(
            anyuser_identity,
            community_id=str(community_id),
        )
        assert results.to_dict()["hits"]["total"] == expected_n_results


# TODO add tests
# test add a record to a community via slug, not only community UUID
# - test corner cases:
#   - no communities passed
#   - too many communities passed
#   - passed a community non-existing
#   - passed a community but the record is already in
#   - passed a community for which a request was already created
#   - passed an invalid record pid: does not exists or it is a draft (not published yet)
# - test what happens there is a request opened, and I create a new version of the record and publish. Everythig works?
#     It should be ok because we work on the parent record. Publish might be blocked because of the `ReviewRequest` class.
#     The draft parent.communities should be updated as the record parent.communities
# - test what happens when including a public record in a public community and in a restricted community


def test_remove_record_from_community_success(
    curator,
    community,
    record_community,
    rdm_record_service,
    service,
    anyuser_identity,
    community_records_service,
):
    """Test removal of a community from a record."""
    data = {"communities": [{"id": community.id}]}
    record = record_community.create_record()
    errors = service.remove(curator.identity, record.pid.pid_value, data)
    assert errors == []

    record_item = rdm_record_service.read(curator.identity, record.pid.pid_value)
    assert not record_item.data["parent"]["communities"]

    # check search results
    results = community_records_service.search(
        anyuser_identity,
        community_id=str(community.id),
    )
    assert results.to_dict()["hits"]["total"] == 0


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

    record_item = rdm_record_service.read(curator.identity, record.pid.pid_value)
    assert record_item.data["parent"]["communities"] == {"ids": [str(community.id)]}


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

    record_item = rdm_record_service.read(curator.identity, record.pid.pid_value)
    assert not record_item.data["parent"]["communities"]


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
    record = record_community.create_record()
    record = add_to_community(db, rdm_record_service, record, community2)
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


# def test_restricted_community_with_public_record(
#     running_app, search_clear, community, record_community, community_service
# ):
#     """Change a community with public records from public to restricted."""
#     identity = running_app.superuser_identity
#     data = community.to_dict()
#     assert data["access"]["visibility"] == "public"
#     data["access"]["visibility"] = "restricted"

#     with pytest.raises(InvalidCommunityVisibility):
#         community_service.update(identity, community.id, data)


# def test_restricted_community_with_restricted_record(
#     running_app, search_clear, community, restricted_record_community, community_service
# ):
#     """Change a community with restricted records from public to restricted."""
#     identity = running_app.superuser_identity
#     # edit the community
#     data = community.to_dict()
#     assert data["access"]["visibility"] == "public"
#     data["access"]["visibility"] = "restricted"

#     comm = community_service.update(identity, community.id, data)
#     assert comm["access"]["visibility"] == "restricted"


# def test_public_community_with_restricted_record(
#     running_app,
#     search_clear,
#     restricted_community,
#     restricted_record_restricted_community,
#     community_service,
# ):
#     """Change a community with restricted records from restricted to public."""
#     identity = running_app.superuser_identity
#     # edit the community
#     data = restricted_community.to_dict()
#     assert data["access"]["visibility"] == "restricted"
#     data["access"]["visibility"] = "public"

#     comm = community_service.update(identity, restricted_community.id, data)
#     assert comm["access"]["visibility"] == "public"


def test_search_communities(
    db,
    service,
    rdm_record_service,
    community,
    community2,
    record_community,
    anyuser_identity,
    minimal_restricted_record,
):
    """."""
    record = record_community.create_record()
    record = add_to_community(db, rdm_record_service, record, community2)

    results = service.search(
        anyuser_identity,
        record.pid.pid_value,
    )
    hits = results.to_dict()["hits"]
    assert hits["total"] == 2
    communities_ids = [str(community.id), str(community2.id)]
    expected = [hits["hits"][0]["id"], hits["hits"][1]["id"]]
    assert sorted(communities_ids) == sorted(expected)

    # test that anonymous cannot search communities in a restricted record
    record = record_community.create_record(record_dict=minimal_restricted_record)
    with pytest.raises(PermissionDeniedError):
        service.search(
            anyuser_identity,
            record.pid.pid_value,
        )
