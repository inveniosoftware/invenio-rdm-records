# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests record's communities resources."""

from copy import deepcopy

import pytest
from invenio_requests.records.api import Request, RequestEvent

from invenio_rdm_records.proxies import (
    current_rdm_records_service,
    current_record_communities_service,
)
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_rdm_records.requests.community_inclusion import CommunityInclusion
from invenio_rdm_records.services.errors import InvalidAccessRestrictions


def _add_to_community(db, record, community):
    record.parent.communities.add(community._record, default=False)
    record.parent.commit()
    record.commit()
    db.session.commit()
    current_rdm_records_service.indexer.index(record, arguments={"refresh": True})
    return record


def test_uploader_add_record_to_communities(
    client,
    uploader,
    record_community,
    headers,
    community,
    open_review_community,
    closed_review_community,
):
    """Test uploader addition of record to open review and closed review community."""
    client = uploader.login(client)

    data = {
        "communities": [
            {"id": open_review_community.id},  # test with id
            {"id": closed_review_community["slug"]},  # test with slug
        ]
    }
    record = record_community.create_record()
    response = client.post(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert not response.json.get("errors")
    processed = response.json["processed"]
    assert len(processed) == 2

    # assert that open review community has been added
    response = client.get(f"/records/{record.pid.pid_value}", headers=headers)
    record_communities_ids = response.json["parent"]["communities"]["ids"]
    assert len(record_communities_ids) == 1
    assert community.id in record_communities_ids
    assert open_review_community.id not in record_communities_ids
    assert closed_review_community.id not in record_communities_ids
    rec_comms = response.json["parent"]["communities"]["entries"]
    assert len(rec_comms) == 1
    assert rec_comms[0]["id"] == str(community.id)
    assert rec_comms[0]["created"] == community["created"]
    assert rec_comms[0]["updated"] == community["updated"]
    assert rec_comms[0]["revision_id"] == community["revision_id"]
    assert rec_comms[0]["slug"] == community["slug"]
    assert rec_comms[0]["metadata"]["title"] == community["metadata"]["title"]
    assert rec_comms[0]["metadata"]["type"]["id"] == community["metadata"]["type"]["id"]
    assert rec_comms[0]["access"] == community["access"]

    # assert that requests are "submitted", but not "accepted"
    for result in processed:
        request_id = result["request_id"]
        response = client.get(
            f"/requests/{request_id}",
            headers=headers,
        )
        assert response.json["status"] == "submitted"
        assert response.json["type"] == CommunityInclusion.type_id
        assert response.json["is_open"] is True

    client = uploader.logout(client)
    # check search results
    for community_id, expected_n_results in [
        (community.id, 1),
        (open_review_community.id, 0),
        (closed_review_community.id, 0),
    ]:
        response = client.get(
            f"/communities/{community_id}/records",
            headers=headers,
        )
        assert response.json["hits"]["total"] == expected_n_results

    # check global search results
    response = client.get("/records", headers=headers)
    assert response.json["hits"]["total"] == 1
    record_hit = response.json["hits"]["hits"][0]
    assert record_hit["id"] == record.pid.pid_value
    assert record_hit["parent"]["communities"]["ids"] == [str(community.id)]
    record_hit_comms = record_hit["parent"]["communities"]["entries"]
    assert len(record_hit_comms) == 1
    assert record_hit_comms[0]["id"] == str(community.id)
    assert record_hit_comms[0]["created"] == community["created"]
    assert record_hit_comms[0]["updated"] == community["updated"]
    assert record_hit_comms[0]["revision_id"] == community["revision_id"]
    assert record_hit_comms[0]["slug"] == community["slug"]
    assert record_hit_comms[0]["metadata"]["title"] == community["metadata"]["title"]
    assert (
        record_hit_comms[0]["metadata"]["type"]["id"]
        == community["metadata"]["type"]["id"]
    )
    assert record_hit_comms[0]["access"] == community["access"]


def test_community_owner_add_record_to_communities(
    client,
    headers,
    curator,
    inviter,
    community,
    open_review_community,
    closed_review_community,
    record_community,
):
    """Test owner inclusion of record to open review and closed review community."""
    client = curator.login(client)

    data = {
        "communities": [
            {"id": open_review_community.id},
            {"id": closed_review_community.id},
        ]
    }
    inviter(curator.id, open_review_community.id, "curator")
    inviter(curator.id, closed_review_community.id, "curator")
    record = record_community.create_record(uploader=curator)
    # create a draft of the record, to ensure that it is included even with a draft
    response = client.post(
        f"/records/{record.pid.pid_value}/draft",
        headers=headers,
    )

    response = client.post(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert not response.json.get("errors")
    processed = response.json["processed"]
    assert len(processed) == 2

    response = client.get(
        f"/records/{record.pid.pid_value}",
        headers=headers,
    )
    record_communities = response.json["parent"]["communities"]["ids"]
    # assert that only the curator's community has been added
    assert len(record_communities) == 2
    assert community.id in record_communities
    assert open_review_community.id in record_communities
    assert closed_review_community.id not in record_communities

    # assert that the request of the curator is "accepted"
    for result in processed:
        community_id = result["community_id"]
        request_id = result["request_id"]
        response = client.get(
            f"/requests/{request_id}",
            headers=headers,
        )
        request = response.json
        assert request["type"] == CommunityInclusion.type_id
        if community_id == open_review_community.id:
            assert request["status"] == "accepted"
            assert request["is_open"] is False
        elif community_id == closed_review_community.id:
            assert request["status"] == "submitted"
            assert request["is_open"] is True
        else:
            raise

    client = curator.logout(client)
    # check search results
    for community_id, expected_n_results in [
        (community.id, 1),
        (open_review_community.id, 1),
        (closed_review_community.id, 0),
    ]:
        response = client.get(
            f"/communities/{community_id}/records",
            headers=headers,
        )
        assert response.json["hits"]["total"] == expected_n_results


def test_community_owner_add_record_to_communities_forcing_review_with_comment(
    client,
    headers,
    curator,
    inviter,
    community,
    open_review_community,
    record_community,
):
    """Test owner addition of record to open review by forcing review with a comment."""
    client = curator.login(client)

    expected_comment = {
        "payload": {"content": "Could someone review it?", "format": "html"}
    }
    data = {
        "communities": [
            {
                "id": open_review_community.id,
                "require_review": True,
                "comment": expected_comment,
            },
        ]
    }
    inviter(curator.id, open_review_community.id, "curator")
    record = record_community.create_record(uploader=curator)

    response = client.post(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert not response.json.get("errors")
    processed = response.json["processed"]
    assert len(processed) == 1

    response = client.get(
        f"/records/{record.pid.pid_value}",
        headers=headers,
    )
    record_communities = response.json["parent"]["communities"]["ids"]
    # assert that the community was not added
    assert len(record_communities) == 1
    assert community.id in record_communities
    assert open_review_community.id not in record_communities

    # assert that the request of the curator is in review ("submitted")
    result = processed[0]
    request_id = result["request_id"]

    Request.index.refresh()
    RequestEvent.index.refresh()

    response = client.get(
        f"/requests/{request_id}",
        headers=headers,
    )
    request = response.json
    assert request["type"] == CommunityInclusion.type_id
    assert request["status"] == "submitted"
    assert request["is_open"] is True

    # check comment
    response = client.get(
        f"/requests/{request_id}/timeline",
        headers=headers,
    )
    comments = response.json
    assert comments["hits"]["total"] == 1
    comment_content = comments["hits"]["hits"][0]["payload"]["content"]
    assert comment_content == expected_comment["payload"]["content"]

    client = curator.logout(client)
    # check search results
    for community_id, expected_n_results in [
        (community.id, 1),
        (open_review_community.id, 0),
    ]:
        response = client.get(
            f"/communities/{community_id}/records",
            headers=headers,
        )
        assert response.json["hits"]["total"] == expected_n_results


def test_restrict_community_before_accepting_inclusion(
    client,
    uploader,
    record_community,
    headers,
    community_owner,
    open_review_community,
):
    """Test should not include when community is changed to restricted before accept."""
    client = uploader.login(client)

    data = {
        "communities": [
            {"id": open_review_community.id},
        ]
    }
    first_version_record = record_community.create_record()

    # create inclusion request
    response = client.post(
        f"/records/{first_version_record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert len(response.json["processed"]) == 1
    request_id = response.json["processed"][0]["request_id"]

    # change the community to restricted
    client = uploader.logout(client)
    client = community_owner.login(client)
    restricted = deepcopy(open_review_community.data)
    restricted["access"]["visibility"] = "restricted"
    response = client.put(
        f"/communities/{open_review_community.id}",
        headers=headers,
        json=restricted,
    )
    assert response.status_code == 200

    # accept request should fail
    # The error handlers for this action are defined in invenio-app-rdm, therefore we catch the exception here
    with pytest.raises(InvalidAccessRestrictions):
        client.post(
            f"/requests/{request_id}/actions/accept",
            headers=headers,
            json={},
        )


def test_create_new_version_after_inclusion_request(
    client,
    uploader,
    record_community,
    headers,
    community_owner,
    open_review_community,
):
    """Test that the new record's version should be in the community after inclusion."""
    client = uploader.login(client)

    data = {
        "communities": [
            {"id": open_review_community.id},
        ]
    }
    first_version_record = record_community.create_record()
    response = client.post(
        f"/records/{first_version_record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert len(response.json["processed"]) == 1
    request_id = response.json["processed"][0]["request_id"]

    # create a new version of the record
    response = client.post(
        f"/records/{first_version_record.pid.pid_value}/versions",
        headers=headers,
        json={},
    )
    assert response.status_code == 201
    second_version_record = response.json
    second_version_record_id = response.json["id"]

    # update title and publication date of the second version
    second_version_record["metadata"]["title"] = "second version"
    second_version_record["metadata"]["publication_date"] = "2023-01-01"
    response = client.put(
        f"/records/{second_version_record_id}/draft",
        headers=headers,
        json=second_version_record,
    )
    assert response.status_code == 200

    # accept the inclusion request of the first version
    client = uploader.logout(client)
    client = community_owner.login(client)
    response = client.post(
        f"/requests/{request_id}/actions/accept",
        headers=headers,
        json={},
    )
    assert response.status_code == 200
    Request.index.refresh()
    RDMRecord.index.refresh()

    # check search results, first version should be in
    client = uploader.logout(client)
    client = community_owner.logout(client)
    response = client.get(
        f"/communities/{open_review_community.id}/records",
        headers=headers,
    )
    assert response.json["hits"]["total"] == 1
    hit = response.json["hits"]["hits"][0]
    assert hit["id"] == first_version_record["id"]
    assert hit["metadata"]["title"] == first_version_record["metadata"]["title"]

    # publish the new version of the record
    client = community_owner.logout(client)
    client = uploader.login(client)
    response = client.post(
        f"/records/{second_version_record_id}/draft/actions/publish",
        headers=headers,
        json={},
    )
    assert response.status_code == 202
    second_version_record_id = response.json["id"]
    Request.index.refresh()
    RDMRecord.index.refresh()

    # check search results, second version should be in
    client = uploader.logout(client)
    client = community_owner.logout(client)
    response = client.get(
        f"/communities/{open_review_community.id}/records",
        headers=headers,
    )
    assert response.json["hits"]["total"] == 1
    hit = response.json["hits"]["hits"][0]
    assert hit["id"] == second_version_record_id
    assert hit["metadata"]["title"] == second_version_record["metadata"]["title"]


def test_accept_public_record_in_restricted_community(
    client,
    record_community,
    headers,
    restricted_community,
    community_owner,
):
    """Test accept public record in restricted community."""
    client = community_owner.login(client)

    data = {
        "communities": [
            {"id": restricted_community.id},
        ]
    }
    record = record_community.create_record()
    response = client.post(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert response.json["processed"]
    assert len(response.json["processed"]) == 1
    request_id = response.json["processed"][0]["request_id"]

    # The error handlers for this action are defined in invenio-app-rdm, therefore we catch the exception here
    with pytest.raises(InvalidAccessRestrictions):
        client.post(
            f"/requests/{request_id}/actions/accept",
            headers=headers,
            json={},
        )


def test_include_community_already_in(
    client,
    uploader,
    record_community,
    headers,
    community,
):
    """Test cannot include to a community already included."""
    client = uploader.login(client)

    data = {
        "communities": [
            {"id": community.id},
        ]
    }
    record = record_community.create_record()
    response = client.post(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 400
    assert "already included" in response.json["errors"][0]["message"]


def test_include_community_already_request_open(
    client,
    uploader,
    record_community,
    headers,
    open_review_community,
):
    """Test cannot include multiple times."""
    client = uploader.login(client)

    data = {
        "communities": [
            {"id": open_review_community.id},
        ]
    }
    record = record_community.create_record()
    # first inclusion: success
    response = client.post(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert not response.json.get("errors")
    processed = response.json["processed"]
    assert len(processed) == 1

    # second inclusion: error
    response = client.post(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 400
    assert "already an open inclusion request" in response.json["errors"][0]["message"]
    assert not response.json.get("processed")


def test_invalid_record_or_draft(
    client,
    headers,
    uploader,
    community,
    minimal_record,
):
    """Test invalid record."""
    client = uploader.login(client)

    data = {
        "communities": [
            {"id": community.id},
        ]
    }

    response = client.post(
        "/records/not-existing/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 404

    draft = RDMDraft.create(minimal_record)
    response = client.post(
        f"/records/{draft.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 404


def test_remove_community(
    client, uploader, curator, record_community, headers, community
):
    """Test removal of a community from the record."""
    for user in [uploader, curator]:
        record = record_community.create_record()

        data = {"communities": [{"id": community.id}]}
        client = user.login(client)
        response = client.delete(
            f"/records/{record.pid.pid_value}/communities",
            headers=headers,
            json=data,
        )
        assert response.status_code == 200
        assert not response.json.get("errors")
        record_saved = client.get(f"/records/{record.pid.pid_value}", headers=headers)
        assert not record_saved.json["parent"]["communities"]

        client = user.logout(client)
        # check search results
        response = client.get(
            f"/communities/{community.id}/records",
            headers=headers,
        )
        assert response.json["hits"]["total"] == 0


def test_remove_missing_permission(
    client, test_user, record_community, headers, community
):
    """Test remove of a community from the record by an unauthorized user."""
    data = {"communities": [{"id": community.id}]}

    client = test_user.login(client)
    record = record_community.create_record()

    response = client.delete(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 400
    assert len(response.json["errors"]) == 1
    record_saved = client.get(f"/records/{record.pid.pid_value}", headers=headers)
    assert record_saved.json["parent"]["communities"]["ids"] == [str(community.id)]


def test_remove_existing_non_existing_community(
    client, uploader, record_community, headers, community
):
    """Test remove of an existing and a non-existing community from the record."""
    data = {"communities": [{"id": "wrong-id"}, {"id": community.id}]}

    client = uploader.login(client)
    record = record_community.create_record()

    response = client.delete(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert len(response.json["errors"]) == 1
    record_saved = client.get(f"/records/{record.pid.pid_value}", headers=headers)
    assert not record_saved.json["parent"]["communities"]


@pytest.mark.parametrize(
    "payload",
    (
        [{"id": "wrong-id"}],
        [{"id": "duplicated-id"}, {"id": "duplicated-id"}],
        [],
    ),
)
def test_add_remove_non_existing_community(
    client, uploader, record_community, headers, community, payload
):
    """Test add/remove of a non-existing community from the record."""
    data = {"communities": payload}

    client = uploader.login(client)
    record = record_community.create_record()
    for operation in [client.post, client.delete]:
        response = operation(
            f"/records/{record.pid.pid_value}/communities",
            headers=headers,
            json=data,
        )
        assert response.status_code == 400
        record_saved = client.get(f"/records/{record.pid.pid_value}", headers=headers)
        assert record_saved.json["parent"]["communities"]["ids"] == [str(community.id)]


def test_remove_another_community(
    client,
    headers,
    db,
    curator,
    community2,
    record_community,
):
    """Test error when removing a community by a curator of another community."""
    client = curator.login(client)
    record = record_community.create_record()
    record = _add_to_community(db, record, community2)
    # record is part of `community` and `community2`
    # curator is curator of `community`: it cannot remove it from `community2`

    data = {"communities": [{"id": community2.id}]}
    response = client.delete(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 400
    errors = response.json["errors"]

    assert len(errors) == 1
    assert errors[0]["community"] == community2.id
    assert errors[0]["message"] == "Permission denied."


def test_add_remove_exceeded_max_number_of_communities(
    client, uploader, record_community, headers, community
):
    """Test raise exceeded max number of communities."""
    client = uploader.login(client)
    record = record_community.create_record()

    random_community = {"id": "random-id"}
    lots_of_communities = []
    while (
        len(lots_of_communities)
        <= current_record_communities_service.config.max_number_of_removals
    ):
        lots_of_communities.append(random_community)
    data = {"communities": lots_of_communities}
    for operation in [client.post, client.delete]:
        response = operation(
            f"/records/{record.pid.pid_value}/communities",
            headers=headers,
            json=data,
        )
        assert response.status_code == 400


def test_search_communities(
    client,
    headers,
    db,
    community,
    community2,
    record_community,
    minimal_restricted_record,
):
    """Test search record's communities."""
    record = record_community.create_record()
    record = _add_to_community(db, record, community2)

    response = client.get(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
    )
    hits = response.json["hits"]
    assert hits["total"] == 2
    communities_ids = [str(community.id), str(community2.id)]
    expected = [hits["hits"][0]["id"], hits["hits"][1]["id"]]
    assert sorted(communities_ids) == sorted(expected)

    # test that anonymous cannot search communities in a restricted record
    record = record_community.create_record(record_dict=minimal_restricted_record)
    response = client.get(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
    )
    assert response.status_code == 403


def test_add_record_to_community_submission_closed_non_member(
    client,
    uploader,
    record_community,
    headers,
    community2,
    closed_submission_community,
):
    """Test addition of record to community with closed submission."""
    client = uploader.login(client)

    data = {
        "communities": [
            {"id": community2.id},
            {"id": closed_submission_community.id},
        ]
    }
    record = record_community.create_record()
    response = client.post(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )

    assert response.status_code == 200
    assert (
        response.json["errors"][0]["message"]
        == "Submission to this community is only allowed to community members."
    )
    processed = response.json["processed"]
    assert len(processed) == 1


def test_add_record_to_community_submission_closed_member(
    client,
    community_owner,
    record_community,
    headers,
    community2,
    closed_submission_community,
):
    """Test addition of record to community with closed submission."""
    client = community_owner.login(client)

    data = {
        "communities": [
            {"id": community2.id},
            {"id": closed_submission_community.id},
        ]
    }
    record = record_community.create_record()
    response = client.post(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert not response.json.get("errors")
    processed = response.json["processed"]
    assert len(processed) == 2


def test_add_record_to_community_submission_open_non_member(
    client,
    uploader,
    record_community,
    headers,
    community2,
):
    """Test addition of record to community with open submission."""
    client = uploader.login(client)

    data = {
        "communities": [
            {"id": community2.id},
        ]
    }
    record = record_community.create_record()
    response = client.post(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert not response.json.get("errors")
    processed = response.json["processed"]
    assert len(processed) == 1


def test_add_record_to_restricted_community_submission_open_non_member(
    client,
    uploader,
    record_community,
    headers,
    restricted_community,
):
    """Test addition of record to restricted community with open submission."""
    client = uploader.login(client)

    data = {
        "communities": [
            {"id": restricted_community.id},
        ]
    }
    record = record_community.create_record()
    response = client.post(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 400
    assert (
        response.json["errors"][0]["message"]
        == "Submission to this community is only allowed to community members."
    )
    assert not response.json.get("processed")


def test_add_record_to_restricted_community_submission_open_member(
    client,
    community_owner,
    record_community,
    headers,
    restricted_community,
):
    """Test addition of record to restricted community with open submission."""
    client = community_owner.login(client)

    data = {
        "communities": [
            {"id": restricted_community.id},
        ]
    }
    record = record_community.create_record()
    response = client.post(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert not response.json.get("errors")
    processed = response.json["processed"]
    assert len(processed) == 1
