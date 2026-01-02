# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Records-Permissions is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from flask_principal import Identity, UserNeed
from invenio_access.permissions import any_user, authenticated_user, system_process
from invenio_communities.generators import CommunityRoleNeed
from invenio_communities.members.records.api import Member
from invenio_db import db
from invenio_records_permissions.generators import (
    AnyUser,
    AuthenticatedUser,
    SystemProcess,
)
from invenio_requests import current_requests_service

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records import RDMParent, RDMRecord
from invenio_rdm_records.records.api import RDMDraft
from invenio_rdm_records.records.systemfields.draft_status import DraftStatus
from invenio_rdm_records.requests.community_submission import CommunitySubmission
from invenio_rdm_records.services.generators import (
    IfRestricted,
    RecordOwners,
    RequestReviewers,
)


@pytest.fixture()
def draft_for_open_review(
    minimal_record, open_review_community, service, community_owner, db
):
    minimal_record["parent"] = {
        "review": {
            "type": CommunitySubmission.type_id,
            "receiver": {"community": open_review_community.data["id"]},
        }
    }

    # Create draft with review
    return service.create(community_owner.identity, minimal_record)


def get_community_owner_identity(community):
    """Get the identity for the first owner of the community."""
    members = Member.get_members(community.id)
    for m in members:
        if m.role == "owner":
            owner_id = m.user_id
            identity = Identity(owner_id)
            identity.provides.add(any_user)
            identity.provides.add(authenticated_user)
            identity.provides.add(CommunityRoleNeed(str(community.id), "owner"))
            identity.provides.add(UserNeed(owner_id))
            return identity


@pytest.fixture()
def service():
    """Get the current RDM records service."""
    return current_rdm_records.records_service


def _public_record():
    record = RDMRecord({}, access={})
    record.access.protection.set("public", "public")
    return record


def _restricted_record():
    record = RDMRecord({}, access={})
    record.access.protection.set("restricted", "restricted")
    return record


def _owned_record():
    parent = RDMParent.create({})
    parent.access.owner = {"user": 16}
    record = RDMRecord.create({}, parent=parent)
    return record


def _then_needs():
    return {authenticated_user, system_process}


def _else_needs():
    return {any_user, system_process}


#
# Tests
#
@pytest.mark.parametrize(
    "field,record_fun,expected_needs_fun",
    [
        ("record", _public_record, _else_needs),
        ("record", _restricted_record, _then_needs),
        ("files", _public_record, _else_needs),
        ("files", _restricted_record, _then_needs),
    ],
)
def test_ifrestricted_needs(field, record_fun, expected_needs_fun):
    """Test the IfRestricted generator."""
    generator = IfRestricted(
        field,
        then_=[AuthenticatedUser(), SystemProcess()],
        else_=[AnyUser(), SystemProcess()],
    )
    assert generator.needs(record=record_fun()) == expected_needs_fun()
    assert generator.excludes(record=record_fun()) == set()


def test_ifrestricted_query():
    """Test the query generation."""
    generator = IfRestricted("record", then_=[AuthenticatedUser()], else_=[AnyUser()])
    assert generator.query_filter(identity=any_user).to_dict() == {
        "bool": {
            "should": [
                {"match": {"access.record": "restricted"}},
                {"match": {"access.record": "public"}},
            ]
        }
    }


def test_record_owner(app, mocker):
    generator = RecordOwners()
    record = _owned_record()

    assert generator.needs(record=record) == [UserNeed(16)]

    assert generator.excludes(record=record) == []

    # Anonymous identity.
    assert not generator.query_filter(identity=mocker.Mock(provides=[]))

    # Authenticated identity
    query_filter = generator.query_filter(
        identity=mocker.Mock(provides=[mocker.Mock(method="id", value=15)])
    )

    expected_query_filter = {"terms": {"parent.access.owned_by.user": [15]}}
    assert query_filter.to_dict() == expected_query_filter


def test_request_reviewers(
    draft_for_open_review, open_review_community, service, users
):
    """Test direct publish review for community owner."""
    assert (
        draft_for_open_review["status"]
        == DraftStatus.review_to_draft_statuses["created"]
    )
    identity = get_community_owner_identity(open_review_community)

    req = service.review.submit(identity, draft_for_open_review.id, require_review=True)
    current_requests_service.update(
        identity, req.id, {"reviewers": [{"user": str(users[0].id)}]}
    )

    req = current_requests_service.read(identity, req.id).to_dict()
    record = service.draft_cls.pid.resolve(
        draft_for_open_review["id"], registered_only=False
    )
    generator = RequestReviewers()
    assert generator.needs(record=record) == [UserNeed(users[0].id)]
