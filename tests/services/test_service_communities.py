# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test record's communities service."""

import pytest
from invenio_communities.proxies import current_communities
from invenio_communities.generators import CommunityMembers
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests import current_events_service, current_requests_service
from marshmallow import ValidationError

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.errors import InvalidCommunityVisibility


@pytest.fixture()
def community_records_service():
    """Get the current records communities service."""
    return current_rdm_records.community_records_service


@pytest.fixture()
def community_service():
    """Get the current communities service."""
    return current_communities.service


def test_search_record_suggested_communities(
    db,
    service,
    rdm_record_service,
    community,
    community2,
    record_community,
    open_review_community,
    anyuser_identity,
    uploader,
    inviter,
):
    """Test search of suggested communities for a record."""
    inviter(uploader.id, open_review_community.id, "curator")
    record = record_community.create_record()

    # Test permissions
    with pytest.raises(PermissionDeniedError):
        service.search_suggested_communities(
            anyuser_identity,
            record.pid.pid_value,
        )

    # Return user communities that are eligible to upload to.
    results = service.search_suggested_communities(
        uploader.identity,
        record.pid.pid_value,
        extra_filter=CommunityMembers().query_filter(uploader.identity),
    )

    # Check that the only community fetched is the one he was added to
    hits = results.to_dict()["hits"]
    assert hits["total"] == 1
    assert hits["hits"][0]["id"] == open_review_community.id

    # Return communities that are eligible to upload to.
    results = service.search_suggested_communities(
        uploader.identity,
        record.pid.pid_value,
    )
    hits = results
    assert hits.total == 2

    data = {"communities": [{"id": open_review_community.id}]}
    service.add(uploader.identity, record.pid.pid_value, data)

    # Fetch the record again
    fetched_record = rdm_record_service.read(uploader.identity, record.pid.pid_value)
    assert (
        open_review_community.id in fetched_record.data["parent"]["communities"]["ids"]
    )

    results = service.search_suggested_communities(
        uploader.identity,
        record.pid.pid_value,
    )
    # Check that the community recently added is not anymore eligible
    hits = results.to_dict()["hits"]
    assert hits["total"] == 1
    assert hits["hits"][0]["id"] == community2.id

    data = {"communities": [{"id": community2.id}]}
    service.add(uploader.identity, record.pid.pid_value, data)

    # Fetch the record again
    fetched_record = rdm_record_service.read(uploader.identity, record.pid.pid_value)

    assert community2.id not in fetched_record.data["parent"]["communities"]["ids"]

    # Community was not added but request was created thus the community is not anymore eligible to be added.
    results = service.search_suggested_communities(
        uploader.identity,
        record.pid.pid_value,
    )

    hits = results
    assert hits.total == 0


def test_make_community_restricted_with_public_record(
    running_app,
    record_community,
    community,
    community_records_service,
    community_service,
):
    """Change a community with public records from public to restricted."""
    identity = running_app.superuser_identity

    record_community.create_record()
    assert (
        community_records_service.search(
            identity,
            community_id=community.id,
        ).total
        == 1
    )
    data = community.to_dict()
    assert data["access"]["visibility"] == "public"
    # edit the community visibility
    data["access"]["visibility"] = "restricted"

    with pytest.raises(InvalidCommunityVisibility):
        community_service.update(identity, community.id, data)


def test_make_community_restricted_with_restricted_record(
    running_app,
    record_community,
    minimal_restricted_record,
    community,
    community_records_service,
    community_service,
):
    """Change a community with restricted records from public to restricted."""
    identity = running_app.superuser_identity

    record_community.create_record(record_dict=minimal_restricted_record)
    assert (
        community_records_service.search(
            identity,
            community_id=community.id,
        ).total
        == 1
    )
    data = community.to_dict()
    assert data["access"]["visibility"] == "public"
    # edit the community visibility
    data["access"]["visibility"] = "restricted"

    comm = community_service.update(identity, community.id, data)
    assert comm["access"]["visibility"] == "restricted"


def test_make_community_public_with_restricted_record(
    running_app,
    record_community,
    minimal_restricted_record,
    restricted_community,
    community_records_service,
    community_service,
):
    """Change a community with restricted records from restricted to public."""
    identity = running_app.superuser_identity

    record_community.create_record(
        record_dict=minimal_restricted_record, community=restricted_community
    )
    assert (
        community_records_service.search(
            identity,
            community_id=restricted_community.id,
        ).total
        == 1
    )
    data = restricted_community.to_dict()
    assert data["access"]["visibility"] == "restricted"
    # edit the community visibility
    data["access"]["visibility"] = "public"

    comm = community_service.update(identity, restricted_community.id, data)
    assert comm["access"]["visibility"] == "public"
