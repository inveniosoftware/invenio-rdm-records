# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test record's communities service."""

import pytest
from invenio_communities.proxies import current_communities

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
