# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Test community records service."""

import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.services.errors import PermissionDeniedError

from invenio_rdm_records.proxies import (
    current_rdm_records_service,
    current_record_communities_service,
)
from invenio_rdm_records.services.errors import CommunityAlreadyExists


def test_bulk_add_non_authorized_permission(community, uploader, record_factory):
    """Test adding multiple records from a non-authorized user."""
    record = record_factory.create_record(uploader=uploader, community=None)

    with pytest.raises(PermissionDeniedError):
        current_record_communities_service.bulk_add(
            uploader.identity, str(community.id), [record["id"]]
        )


def test_bulk_add_by_system_permission(community, community_owner, record_factory):
    """Test bulk add by system."""
    record = record_factory.create_record(uploader=community_owner, community=None)

    current_record_communities_service.bulk_add(
        system_identity, str(community.id), [record["id"]]
    )

    _rec = current_rdm_records_service.record_cls.pid.resolve(record["id"])
    assert community.id in _rec.parent.communities.ids


def test_bulk_add(community, uploader, record_factory):
    """Test bulk add functionality."""
    TOTAL_RECS = 3
    recs = [
        record_factory.create_record(uploader=uploader, community=None)
        for _ in range(TOTAL_RECS)
    ]

    current_record_communities_service.bulk_add(
        system_identity, str(community.id), [rec["id"] for rec in recs]
    )
    for rec in recs:
        _rec = current_rdm_records_service.record_cls.pid.resolve(rec["id"])
        assert community.id in _rec.parent.communities.ids


def test_bulk_add_already_in_community(community, uploader, record_factory):
    """Test failed addition when the record is already in the community."""
    record = record_factory.create_record(uploader=uploader, community=community)

    assert current_record_communities_service.bulk_add(
        system_identity, str(community.id), [record["id"]]
    ) == [
        {
            "record_id": record["id"],
            "community_id": str(community.id),
            "message": "Community already included.",
        }
    ]
