# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test record's communities service."""

import pytest
from invenio_access.permissions import system_identity
from invenio_communities import current_communities
from invenio_records_resources.services.errors import PermissionDeniedError
from marshmallow import ValidationError

from invenio_rdm_records.proxies import (
    current_rdm_records_service,
    current_record_communities_service,
)
from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.services.errors import MaxNumberCommunitiesExceeded


@pytest.fixture()
def service():
    """Get the current RDM records service."""
    return current_rdm_records_service


@pytest.fixture()
def record_communities_service():
    """Get the current records communities service."""
    return current_record_communities_service


@pytest.fixture()
def record_community(db, uploader, minimal_record, community, service):
    """Creates a record that belongs to a community."""
    # create draft
    community = community._record
    draft = service.create(uploader.identity, minimal_record)
    # publish and get record
    record = RDMRecord.publish(draft._record)
    record.commit()
    record.parent.communities.add(community, default=False)
    record.parent.commit()
    record.commit()
    # Manually register the pid to be able to resolve it
    record.pid.register()
    db.session.commit()
    service.indexer.index(record)
    RDMRecord.index.refresh()
    return record


@pytest.fixture()
def curator(UserFixture, community, app, db):
    """Creates a curator of the community fixture."""
    curator = UserFixture(
        email="curatoruser@inveniosoftware.org",
        password="curatoruser",
    )
    curator.create(app, db)
    invitation_data = {
        "members": [
            {
                "type": "user",
                "id": curator.id,
            }
        ],
        "role": "curator",
        "visible": True,
    }

    current_communities.service.members.add(
        system_identity, community.id, invitation_data
    )
    return curator


def test_remove_community_from_record_success(
    running_app, community, record_community, service, record_communities_service
):
    """Test removal of a community from a record."""
    superuser_identity = running_app.superuser_identity
    data = {"communities": [{"id": community.id}]}
    errors = record_communities_service.delete(
        superuser_identity, record_community.pid.pid_value, data
    )
    assert errors == []

    saved_record = service.read(superuser_identity, record_community.pid.pid_value)
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
    with pytest.raises(PermissionDeniedError):
        record_communities_service.delete(
            test_user.identity, record_community.pid.pid_value, data
        )


def test_owner_permission(
    uploader, community, record_community, record_communities_service
):
    """Test permissions to delete."""
    data = {"communities": [{"id": community.id}]}
    record_communities_service.delete(
        uploader.identity, record_community.pid.pid_value, data
    )


def test_curator_permission(
    curator, community, record_community, record_communities_service
):
    """Test permissions to delete."""
    data = {"communities": [{"id": community.id}]}
    record_communities_service.delete(
        curator.identity, record_community.pid.pid_value, data
    )


def test_remove_community_from_record_error(
    running_app, record_community, service, record_communities_service, community
):
    """Test error on removing a wrong community from a record."""
    superuser_identity = running_app.superuser_identity
    data = {"communities": [{"id": "wrong-id"}]}
    errors = record_communities_service.delete(
        superuser_identity, record_community.pid.pid_value, data
    )
    assert len(errors) == 1

    saved_record = service.read(superuser_identity, record_community.pid.pid_value)
    assert saved_record.data["parent"]["communities"] == {"ids": [str(community.id)]}


def test_remove_community_from_record_success_w_errors(
    running_app, community, record_community, service, record_communities_service
):
    """Test removal of communities from record with errors."""
    superuser_identity = running_app.superuser_identity
    wrong_data = [{"id": "wrong-id"}, {"id": "wrong-id2"}]
    correct_data = [{"id": community.id}]
    data = {"communities": correct_data + wrong_data}
    errors = record_communities_service.delete(
        superuser_identity, record_community.pid.pid_value, data
    )

    assert len(errors) == 2

    saved_record = service.read(superuser_identity, record_community.pid.pid_value)
    assert not saved_record.data["parent"]["communities"]


def test_remove_community_from_record_success_w_errors(
    running_app, community, record_community, record_communities_service
):
    """Test removal of communities from record with errors."""
    superuser_identity = running_app.superuser_identity
    random_community = {"id": "random-id"}
    lots_of_communities = []
    while (
        len(lots_of_communities)
        <= record_communities_service.config.max_number_of_removals
    ):
        lots_of_communities.append(random_community)
    data = {"communities": lots_of_communities}
    with pytest.raises(MaxNumberCommunitiesExceeded):
        record_communities_service.delete(
            superuser_identity, record_community.pid.pid_value, data
        )


def test_remove_community_empty_payload(
    running_app, community, record_community, record_communities_service
):
    """Test removal of communities from record with empty payload."""
    superuser_identity = running_app.superuser_identity
    data = {"communities": []}
    with pytest.raises(ValidationError):
        record_communities_service.delete(
            superuser_identity, record_community.pid.pid_value, data
        )
