# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record communities resources tests."""


def test_search_record_suggested_communities(
    client,
    community,
    community2,
    record_community,
    open_review_community,
    uploader,
    inviter,
    headers,
):
    """Test search of suggested communities for a record."""
    record = record_community.create_record()

    response = client.get(
        f"/records/{record.pid.pid_value}/communities-suggestions",
        headers=headers,
        json={},
    )

    assert response.status_code == 403

    client = uploader.login(client)
    # Return user communities that are eligible to upload to.
    response = client.get(
        f"/records/{record.pid.pid_value}/communities-suggestions",
        headers=headers,
        json={},
    )
    assert response.status_code == 200

    # Check that all communities are suggested
    hits = response.json["hits"]
    assert hits["total"] == 2
    assert hits["hits"][0]["id"] == open_review_community.id

    response = client.get(
        f"/records/{record.pid.pid_value}/communities-suggestions?membership=true",
        headers=headers,
        json={},
    )
    assert response.status_code == 200
    hits = response.json["hits"]
    assert hits["total"] == 0

    # add record to a community
    record = record_community.create_record()
    response = client.post(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json={
            "communities": [
                {"id": open_review_community.id},  # test with id
            ]
        },
    )

    assert response.status_code == 200
    assert response.json["processed"][0]["community_id"] == open_review_community.id

    response = client.get(
        f"/records/{record.pid.pid_value}/communities-suggestions",
        headers=headers,
        json={},
    )
    assert response.status_code == 200

    # Make sure the community is no longer suggested
    hits = response.json["hits"]
    assert hits["total"] == 1
    assert hits["hits"][0]["id"] != open_review_community.id


def test_set_default_community(
    client,
    headers,
    curator,
    inviter,
    community,
    open_review_community,
    closed_review_community,
    record_community,
):
    """Test setting a default community for a record."""
    # Add the curator user to the open review community
    inviter(curator.id, open_review_community.id, "curator")
    record = record_community.create_record(uploader=curator)

    # Login as the curator user
    client = curator.login(client)

    # Add the record to the open review community
    resp = client.post(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json={"communities": [{"id": open_review_community.id}]},
    )
    assert resp.status_code == 200
    assert not resp.json.get("errors")
    processed = resp.json["processed"]
    assert len(processed) == 1

    def _assert_record_in_(communities, default=None):
        resp = client.get(f"/records/{record.pid.pid_value}", headers=headers)
        record_communities = resp.json["parent"]["communities"]
        assert set(record_communities["ids"]) == communities
        if default:
            assert record_communities["default"] == default
        else:
            assert "default" not in record_communities

    _assert_record_in_({community.id, open_review_community.id}, default=None)

    # Set the default community to invalid values
    resp = client.put(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json={"default": closed_review_community.id},
    )
    assert resp.status_code == 400
    assert resp.json["message"] == (
        "Cannot set community as the default. The record has not been added to the community."
    )

    # Set the default community to the open review community
    resp = client.put(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json={"default": open_review_community.id},
    )
    assert resp.status_code == 200
    assert resp.json["communities"]["default"] == open_review_community.id

    _assert_record_in_(
        {community.id, open_review_community.id},
        default=open_review_community.id,
    )

    # Unset the default community
    resp = client.put(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json={"default": None},
    )
    assert resp.status_code == 200
    assert "default" not in resp.json["communities"]

    _assert_record_in_({community.id, open_review_community.id}, default=None)

    # Set the default community to the original community
    resp = client.put(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json={"default": community.id},
    )
    assert resp.status_code == 200
    assert resp.json["communities"]["default"] == community.id

    _assert_record_in_({community.id, open_review_community.id}, default=community.id)

    # Unset the default community using empty string (current wrong behaviour in the UI)
    resp = client.put(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json={"default": ""},
    )
    assert resp.status_code == 200
    assert "default" not in resp.json["communities"]

    _assert_record_in_({community.id, open_review_community.id}, default=None)
