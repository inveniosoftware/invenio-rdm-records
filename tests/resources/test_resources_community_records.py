# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests community records resources."""

import pytest

from invenio_rdm_records.proxies import current_community_records_service


@pytest.fixture()
def service():
    """Get the current community records service."""
    return current_community_records_service


def test_remove_community(client, curator, record_community, headers, community):
    """Remove a record from the community."""
    client = curator.login(client)
    record = record_community.create_record()
    data = {"records": [{"id": record.pid.pid_value}]}

    response = client.delete(
        f"/communities/{community.id}/records",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert not response.json.get("errors")


def test_permission_denied(
    client, uploader, test_user, record_community, headers, community
):
    """Missing permissions when removing a record from the community."""
    record = record_community.create_record()
    data = {"records": [{"id": record.pid.pid_value}]}

    test_user_client = test_user.login(client)

    response_403 = test_user_client.delete(
        f"/communities/{community.id}/records",
        headers=headers,
        json=data,
    )
    assert response_403.status_code == 403


def test_error_data(client, curator, headers, community):
    """Remove a wrong record from the community."""
    data = {"records": [{"id": "wrong-id"}]}

    uploader_client = curator.login(client)

    response = uploader_client.delete(
        f"/communities/{community.id}/records",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert response.json["errors"]


def test_removal_of_multiple_communities_success(
    client, curator, record_community, headers, community
):
    """Remove multiple records from a community."""
    client = curator.login(client)
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

    response = client.delete(
        f"/communities/{community.id}/records",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert not response.json.get("errors")


def test_exceeded_max_number_of_records(
    client, curator, record_community, headers, community, service
):
    """Test raise exceeded max number of records."""
    client = curator.login(client)
    random_record = {"id": "random-id"}
    lots_of_records = []
    while len(lots_of_records) <= service.config.max_number_of_removals:
        lots_of_records.append(random_record)

    data = {"records": lots_of_records}
    response = client.delete(
        f"/communities/{community.id}/records",
        headers=headers,
        json=data,
    )
    assert response.status_code == 400
