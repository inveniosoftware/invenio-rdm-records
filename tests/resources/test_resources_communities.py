# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests record's communities resources."""

from invenio_rdm_records.proxies import current_record_communities_service


def test_remove_community(client, uploader, record_community, headers, community):
    """Test removal of a community from the record."""
    client = uploader.login(client)

    data = {"communities": [{"id": community.id}]}
    record = record_community.create_record()
    response = client.delete(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert not response.json.get("errors")
    record_saved = client.get(f"/records/{record.pid.pid_value}", headers=headers)
    assert not record_saved.json["parent"]["communities"]


def test_permission_denied(
    client, uploader, test_user, record_community, headers, community
):
    """Test remove of a community from the record by an unauthorized user."""
    data = {"communities": [{"id": community.id}]}

    test_user_client = test_user.login(client)
    record = record_community.create_record()

    response = test_user_client.delete(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert len(response.json["errors"]) == 1
    record_saved = client.get(f"/records/{record.pid.pid_value}", headers=headers)
    assert record_saved.json["parent"]["communities"] == {"ids": [str(community.id)]}


def test_error_data(client, uploader, record_community, headers, community):
    """Test remove of a non-existing community from the record."""
    data = {"communities": [{"id": "wrong-id"}]}

    uploader_client = uploader.login(client)
    record = record_community.create_record()

    response = uploader_client.delete(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert len(response.json["errors"]) == 1
    record_saved = client.get(f"/records/{record.pid.pid_value}", headers=headers)
    assert record_saved.json["parent"]["communities"] == {"ids": [str(community.id)]}


def test_exceeded_max_number_of_communities(
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
    response = client.delete(
        f"/records/{record.pid.pid_value}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 400


# TODO once upload to multiple communities is implemented
def test_removal_of_multiple_communities():
    """Remove multiple communities from a record."""
    pass
