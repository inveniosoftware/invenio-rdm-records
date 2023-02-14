# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests record's communities resources."""

from invenio_rdm_records.proxies import current_record_communities_service
from tests.resources.conftest import link


def test_remove_community(client, uploader, community_record, headers, community):
    """Remove a community from the record."""
    client = uploader.login(client)

    data = {"communities": [{"id": community.id}]}
    record = community_record.create_record()
    response = client.delete(
        f"/records/{record.id}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert not response.json.get("errors")
    record_saved = client.get(link(record.links["self"]), headers=headers)
    assert not record_saved.json["parent"]["communities"]


def test_permission_denied(
    client, uploader, test_user, community_record, headers, community
):
    """Remove a community from the record."""
    data = {"communities": [{"id": community.id}]}

    test_user_client = test_user.login(client)
    record = community_record.create_record()

    response_403 = test_user_client.delete(
        f"/records/{record.id}/communities",
        headers=headers,
        json=data,
    )
    assert response_403.status_code == 403
    record_saved = client.get(link(record.links["self"]), headers=headers)
    assert record_saved.json["parent"]["communities"] == {"ids": [str(community.id)]}


def test_error_data(client, uploader, community_record, headers, community):
    """Remove a community from the record."""
    data = {"communities": [{"id": "wrong-id"}]}

    uploader_client = uploader.login(client)
    record = community_record.create_record()

    response = uploader_client.delete(
        f"/records/{record.id}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert response.json["errors"]
    record_saved = client.get(link(record.links["self"]), headers=headers)
    assert record_saved.json["parent"]["communities"] == {"ids": [str(community.id)]}


def test_exceeded_max_number_of_communities(
    client, uploader, community_record, headers, community
):
    """Test raise exceeded max number of communities."""
    client = uploader.login(client)
    record = community_record.create_record()

    random_community = {"id": "random-id"}
    lots_of_communities = []
    while (
        len(lots_of_communities)
        <= current_record_communities_service.config.max_number_of_removals
    ):
        lots_of_communities.append(random_community)
    data = {"communities": lots_of_communities}
    response = client.delete(
        f"/records/{record.id}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 400


# TODO once upload to multiple communities is implemented
def test_removal_of_multiple_communities():
    """Remove multiple communities from a record."""
    pass
