# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test record's communities service."""

import pytest
from invenio_records_resources.services.errors import PermissionDeniedError
from marshmallow import ValidationError

from invenio_rdm_records.proxies import current_record_communities_service
from invenio_rdm_records.services.errors import MaxNumberCommunitiesExceeded


@pytest.fixture()
def record_communities_service():
    """Get the current records communities service."""
    return current_record_communities_service


def test_remove_community_from_record_success(
    running_app,
    community,
    record_community,
    rdm_record_service,
    record_communities_service,
):
    """Test removal of a community from a record."""
    superuser_identity = running_app.superuser_identity
    data = {"communities": [{"id": community.id}]}
    record = record_community.create_record()
    errors = record_communities_service.delete(
        superuser_identity, record.pid.pid_value, data
    )
    assert errors == []

    saved_record = rdm_record_service.read(superuser_identity, record.pid.pid_value)
    assert not saved_record.data["parent"]["communities"]


def test_remove_multiple_communities():
    """Test removal of multiple communities of a record."""
    # TODO once the multiple publish is implemented.
    pass


def test_missing_permission(
    test_user, community, record_community, record_communities_service
):
    """Test permissions to delete."""
    data = {"communities": [{"id": community.id}]}
    record = record_community.create_record()

    with pytest.raises(PermissionDeniedError):
        record_communities_service.delete(
            test_user.identity, record.pid.pid_value, data
        )


def test_owner_permission(
    uploader, community, record_community, record_communities_service
):
    """Test permissions to delete."""
    data = {"communities": [{"id": community.id}]}
    record = record_community.create_record()

    record_communities_service.delete(uploader.identity, record.pid.pid_value, data)


def test_curator_permission(
    curator, community, record_community, record_communities_service
):
    """Test permissions to delete."""
    data = {"communities": [{"id": community.id}]}
    record = record_community.create_record()

    record_communities_service.delete(curator.identity, record.pid.pid_value, data)


def test_remove_community_from_record_error(
    running_app,
    record_community,
    rdm_record_service,
    record_communities_service,
    community,
):
    """Test error on removing a wrong community from a record."""
    superuser_identity = running_app.superuser_identity
    data = {"communities": [{"id": "wrong-id"}]}
    record = record_community.create_record()

    errors = record_communities_service.delete(
        superuser_identity, record.pid.pid_value, data
    )
    assert len(errors) == 1

    saved_record = rdm_record_service.read(superuser_identity, record.pid.pid_value)
    assert saved_record.data["parent"]["communities"] == {"ids": [str(community.id)]}


def test_remove_community_from_record_success_w_errors(
    running_app,
    community,
    record_community,
    rdm_record_service,
    record_communities_service,
):
    """Test removal of communities from record with errors."""
    superuser_identity = running_app.superuser_identity
    wrong_data = [{"id": "wrong-id"}, {"id": "wrong-id2"}]
    correct_data = [{"id": community.id}]
    data = {"communities": correct_data + wrong_data}
    record = record_community.create_record()

    errors = record_communities_service.delete(
        superuser_identity, record.pid.pid_value, data
    )

    assert len(errors) == 2

    saved_record = rdm_record_service.read(
        superuser_identity, record_community.pid.pid_value
    )
    assert not saved_record.data["parent"]["communities"]


def test_remove_community_from_record_success_w_errors(
    running_app, community, record_community, record_communities_service
):
    """Test removal of communities from record with errors."""
    superuser_identity = running_app.superuser_identity
    random_community = {"id": "random-id"}
    record = record_community.create_record()

    lots_of_communities = []
    while (
        len(lots_of_communities)
        <= record_communities_service.config.max_number_of_removals
    ):
        lots_of_communities.append(random_community)
    data = {"communities": lots_of_communities}
    with pytest.raises(MaxNumberCommunitiesExceeded):
        record_communities_service.delete(
            superuser_identity, record.pid.pid_value, data
        )


def test_remove_community_empty_payload(
    running_app, community, record_community, record_communities_service
):
    """Test removal of communities from record with empty payload."""
    superuser_identity = running_app.superuser_identity
    data = {"communities": []}
    record = record_community.create_record()

    with pytest.raises(ValidationError):
        record_communities_service.delete(
            superuser_identity, record.pid.pid_value, data
        )
