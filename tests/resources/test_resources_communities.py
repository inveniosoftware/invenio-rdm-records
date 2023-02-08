# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests record's communities resources."""

import pytest

from invenio_rdm_records.proxies import current_rdm_records_service
from tests.resources.conftest import link


@pytest.fixture()
def service():
    """Get the current RDM records service."""
    return current_rdm_records_service


@pytest.fixture()
def record(uploader, minimal_record, community, service, running_app, db):
    """Record that belongs to a community."""
    # Create draft with review
    draft = service.create(uploader.identity, minimal_record)
    # Publish
    record = service.publish(uploader.identity, draft.id)
    # TODO replace the following code by the service func that adds the record to a community
    community = community._record
    record._record.parent.communities.add(community, default=False)
    record._record.parent.commit()
    db.session.commit()
    service.indexer.index(record._record)
    return record


def test_remove_community(client, uploader, record, headers, community):
    """Remove a community from the record."""
    client = uploader.login(client)

    data = {"communities": [{"id": community.id}]}
    response = client.delete(
        f"/records/{record.id}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert not response.json.get("errors")
    record_saved = client.get(link(record.links["self"]), headers=headers)
    assert not record_saved.json["parent"]["communities"]


def test_permission_denied(client, uploader, test_user, record, headers, community):
    """Remove a community from the record."""
    data = {"communities": [{"id": community.id}]}

    test_user_client = test_user.login(client)

    response_403 = test_user_client.delete(
        f"/records/{record.id}/communities",
        headers=headers,
        json=data,
    )
    assert response_403.status_code == 403
    record_saved = client.get(link(record.links["self"]), headers=headers)
    assert record_saved.json["parent"]["communities"] == {"ids": [str(community.id)]}


def test_error_data(client, uploader, record, headers, community):
    """Remove a community from the record."""
    data = {"communities": [{"id": "wrong-id"}]}

    uploader_client = uploader.login(client)

    response = uploader_client.delete(
        f"/records/{record.id}/communities",
        headers=headers,
        json=data,
    )
    assert response.status_code == 200
    assert response.json["errors"]
    record_saved = client.get(link(record.links["self"]), headers=headers)
    assert record_saved.json["parent"]["communities"] == {"ids": [str(community.id)]}


# TODO once upload to multiple communities is implemented
def test_removal_of_multiple_communities():
    """Remove multiple communities from a record."""
    pass
