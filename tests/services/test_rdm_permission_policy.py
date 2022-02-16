# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Test RDMRecordPermissionPolicy."""

from copy import deepcopy

import pytest
from invenio_communities import current_communities
from invenio_communities.communities.records.api import Community
from invenio_communities.permissions import CommunityRoleManager

from invenio_rdm_records.services import RDMRecordPermissionPolicy


@pytest.fixture()
def owner(UserFixture, app, db):
    """Owner."""
    u = UserFixture(
        email="owner@inveniosoftware.org",
        password="owner",
    )
    u.create(app, db)
    return u


@pytest.fixture()
def community(running_app, owner, minimal_community):
    """Get the current RDM records service."""
    c = current_communities.service.create(
        owner.identity,
        minimal_community,
    )._record
    Community.index.refresh()
    return c


@pytest.fixture()
def community_draft(minimal_record, community, service, running_app):
    minimal_record['parent'] = {
        'review': {
            'type': 'community-submission',
            'receiver': {'community': community.id}
        }
    }

    return service.create(
        running_app.superuser_identity,
        minimal_record
    )._record


@pytest.fixture()
def community_record(community_draft, requests_service, running_app, service):
    req = service.review.submit(
        running_app.superuser_identity, community_draft.pid.pid_value
    )
    req = requests_service.execute_action(
        running_app.superuser_identity,
        req.id,
        'accept',
        {}
    )
    return service.read(
        running_app.superuser_identity, community_draft.pid.pid_value
    )._record


@pytest.fixture(scope="module")
def make_member_identity():
    """Create an identity with community member+role needs."""

    def _make_member_identity(identity, community, role=None):
        """Create new identity from identity."""
        i = deepcopy(identity)
        i.provides.add(
            CommunityRoleManager(community.id, "member").to_need()
        )

        if role:
            i.provides.add(
                CommunityRoleManager(community.id, role).to_need()
            )

        return i

    return _make_member_identity


@pytest.fixture()
def create_community_identity(UserFixture, app, db, make_member_identity):
    """Create a community identity."""
    i = 0

    def _create_community_identity(community, role=None):
        """Creating function."""
        nonlocal i  # Needed to close over i
        u = UserFixture(
            email=f"{i}@inveniosoftware.org",
            password="password",
        )
        u.create(app, db)
        identity = make_member_identity(u.identity, community, role)
        i += 1
        return identity

    return _create_community_identity


@pytest.fixture(scope="module")
def policy():
    """Policy under test."""
    return RDMRecordPermissionPolicy


def test_owner_manager_curator_can_update_record_of_community(
        community_draft, community_record, community,
        create_community_identity, policy):
    owner_identity = create_community_identity(community, "owner")
    manager_identity = create_community_identity(community, "manager")
    curator_identity = create_community_identity(community, "curator")
    member_identity = create_community_identity(community)
    can_identities = [owner_identity, manager_identity, curator_identity]
    cant_identities = [member_identity]

    # Put published community record in draft mode
    for i in can_identities:
        assert policy(action='edit', record=community_record).allows(i)
    for i in cant_identities:
        assert not policy(action='edit', record=community_record).allows(i)

    # Read draft
    for i in can_identities:
        assert policy(action='read_draft', record=community_draft).allows(i)
    for i in cant_identities:
        assert not (
            policy(action='read_draft', record=community_draft).allows(i)
        )

    # Edit draft
    for i in can_identities:
        assert policy(action='update_draft', record=community_draft).allows(i)
    for i in cant_identities:
        assert not (
            policy(action='update_draft', record=community_draft).allows(i)
        )

    # Publish
    for i in can_identities:
        assert policy(action='publish', record=community_draft).allows(i)
    for i in cant_identities:
        assert not (
            policy(action='publish', record=community_draft).allows(i)
        )


def test_owner_manager_curator_can_create_new_version(
        community_record, community, create_community_identity, policy):
    owner_identity = create_community_identity(community, "owner")
    manager_identity = create_community_identity(community, "manager")
    curator_identity = create_community_identity(community, "curator")
    member_identity = create_community_identity(community)
    can_identities = [owner_identity, manager_identity, curator_identity]
    cant_identities = [member_identity]

    # Create new versions
    for i in can_identities:
        assert policy(action='new_version', record=community_record).allows(i)
    for i in cant_identities:
        assert not (
            policy(action='new_version', record=community_record).allows(i)
        )


@pytest.fixture()
def restricted_community_record(
        community, minimal_record, service, running_app, requests_service):
    minimal_record['parent'] = {
        'review': {
            'type': 'community-submission',
            'receiver': {'community': community.id}
        }
    }
    minimal_record["access"] = {
        "record": "restricted",
        "files": "restricted",
    }
    draft = service.create(
        running_app.superuser_identity,
        minimal_record
    )._record

    req = service.review.submit(
        running_app.superuser_identity, draft.pid.pid_value
    )
    req = requests_service.execute_action(
        running_app.superuser_identity,
        req.id,
        'accept',
        {}
    )
    return service.read(
        running_app.superuser_identity, draft.pid.pid_value
    )._record


def test_member_can_see_restricted_record(
        anyuser_identity, community, create_community_identity,
        restricted_community_record, policy):
    member_identity = create_community_identity(community)
    can_identities = [member_identity]
    cant_identities = [anyuser_identity]

    # See restricted record
    for i in can_identities:
        assert policy(
            action='read', record=restricted_community_record
        ).allows(i)
    for i in cant_identities:
        assert not (
            policy(action='read', record=restricted_community_record).allows(i)
        )

    # See restricted record files
    for i in can_identities:
        assert policy(
            action='read_files', record=restricted_community_record
        ).allows(i)
    for i in cant_identities:
        assert not (
            policy(
                action='read_files', record=restricted_community_record
            ).allows(i)
        )
