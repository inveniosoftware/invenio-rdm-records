# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test of the review deposit integration."""

import pytest
from flask_principal import Identity
from invenio_access.permissions import any_user, authenticated_user
from invenio_communities import current_communities
from invenio_communities.communities.records.api import Community
from invenio_communities.generators import CommunityRoleNeed
from invenio_communities.members.records.api import Member
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests import current_requests_service
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm.exc import NoResultFound

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records.api import RDMDraft
from invenio_rdm_records.records.systemfields.draft_status import DraftStatus
from invenio_rdm_records.services.errors import (
    ReviewExistsError,
    ReviewInconsistentAccessRestrictions,
    ReviewNotFoundError,
    ReviewStateError,
)


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
            return identity


@pytest.fixture()
def service():
    """Get the current RDM records service."""
    return current_rdm_records.records_service


@pytest.fixture()
def requests_service():
    """Get the current RDM requests service."""
    return current_requests_service


@pytest.fixture()
def community2(running_app, minimal_community2, db):
    """Get the current RDM records service."""
    return current_communities.service.create(
        running_app.superuser_identity,
        minimal_community2,
    )


@pytest.fixture()
def draft(minimal_record, community, service, running_app, db):
    minimal_record["parent"] = {
        "review": {
            "type": "community-submission",
            "receiver": {"community": community.data["id"]},
        }
    }

    # Create draft with review
    return service.create(running_app.superuser_identity, minimal_record)


@pytest.fixture()
def public_draft_review_restricted(
    minimal_record, restricted_community, service, running_app, db
):
    minimal_record["parent"] = {
        "review": {
            "type": "community-submission",
            "receiver": {"community": restricted_community.data["id"]},
        }
    }

    # Create draft with review
    return service.create(running_app.superuser_identity, minimal_record)


@pytest.fixture()
def restricted_draft_review_restricted(
    minimal_restricted_record, restricted_community, service, running_app, db
):
    minimal_restricted_record["parent"] = {
        "review": {
            "type": "community-submission",
            "receiver": {"community": restricted_community.data["id"]},
        }
    }

    # Create draft with review
    return service.create(running_app.superuser_identity, minimal_restricted_record)


#
# Tests
#
def test_simple_flow(draft, running_app, community, service, requests_service):
    """Test basic creation with review."""
    # check draft status
    assert draft["status"] == DraftStatus.review_to_draft_statuses["created"]

    # ### Submit draft for review
    req = service.review.submit(running_app.superuser_identity, draft.id).to_dict()
    assert req["status"] == "submitted"
    assert req["title"] == draft["metadata"]["title"]

    # check draft status
    draft = service.read_draft(running_app.superuser_identity, draft.id)
    assert (
        draft.to_dict()["status"] == DraftStatus.review_to_draft_statuses["submitted"]
    )

    # ### Read request as curator
    # TODO: test that curator can search/read the request
    # TODO: check links - curator should not see cancel link

    # ### Accept request
    req = requests_service.execute_action(
        running_app.superuser_identity, req["id"], "accept", {}
    ).to_dict()
    assert req["status"] == "accepted"
    assert req["is_open"] is False

    # ### Read the record
    record = service.read(running_app.superuser_identity, draft.id).to_dict()
    assert "review" not in record["parent"]  # Review was desassociated
    assert record["is_published"] is True
    assert record["parent"]["communities"]["ids"] == [community.data["id"]]
    assert record["parent"]["communities"]["default"] == community.data["id"]
    assert record["status"] == "published"

    # ### Read draft (which should have been removed)
    with pytest.raises(NoResultFound):
        service.read_draft(running_app.superuser_identity, draft.id)

    # ### Create a new version (still part of community)
    draft = service.new_version(running_app.superuser_identity, draft.id).to_dict()
    assert "review" not in draft["parent"]
    assert draft["parent"]["communities"]["ids"] == [community.data["id"]]
    assert draft["parent"]["communities"]["default"] == community.data["id"]
    assert draft["status"] == "new_version_draft"


def test_creation(draft, running_app, community, service, requests_service):
    """Test basic creation with review."""
    # See the draft fixture for the actual creation
    record_id = draft.id
    parent = draft.to_dict()["parent"]

    assert "id" in parent["review"]
    assert parent["review"]["type"] == "community-submission"
    assert parent["review"]["receiver"] == {"community": community.data["id"]}
    assert "@v" not in parent["review"]  # internals should not be exposed

    # Read review request (via request service)
    review = requests_service.read(
        running_app.superuser_identity, parent["review"]["id"]
    ).to_dict()

    assert review["id"] == parent["review"]["id"]
    assert review["status"] == "created"
    assert review["type"] == "community-submission"
    assert review["receiver"] == {"community": community.data["id"]}
    assert review["created_by"] == {"user": str(running_app.superuser_identity.id)}
    assert review["topic"] == {"record": record_id}

    # Read review request (via record review subservice)
    review = service.review.read(
        running_app.superuser_identity,
        record_id,
    ).to_dict()
    assert review["id"] == parent["review"]["id"]

    # TODO: Test that curator cannot see it yet


def test_create_with_invalid_community(minimal_record, running_app, service):
    """Test with invalid communities."""
    minimal_record["parent"] = {
        "review": {
            "type": "community-submission",
            "receiver": {"community": "00000000-0000-0000-0000-000000000000"},
        }
    }
    pytest.raises(
        NoResultFound,
        service.create,
        running_app.superuser_identity,
        minimal_record,
    )

    minimal_record["parent"] = {
        "review": {"type": "community-submission", "receiver": {"community": "invalid"}}
    }
    pytest.raises(
        NoResultFound,
        service.create,
        running_app.superuser_identity,
        minimal_record,
    )


def test_create_review_after_draft(running_app, community, service, minimal_record):
    """Test creation of review after draft was created."""
    # Create draft
    draft = service.create(running_app.superuser_identity, minimal_record)
    assert draft.to_dict()["status"] == "draft"

    # Then create review (you use update, not create for this).
    data = {
        "type": "community-submission",
        "receiver": {"community": community.data["id"]},
    }
    req = service.review.update(
        running_app.superuser_identity,
        draft.id,
        data,
        revision_id=draft.data["revision_id"],
    ).to_dict()
    assert req["status"] == "created"
    assert req["topic"] == {"record": draft.id}
    assert req["receiver"] == {"community": community.data["id"]}

    # check draft status
    draft = service.read_draft(running_app.superuser_identity, draft.id).to_dict()
    assert draft["status"] == DraftStatus.review_to_draft_statuses[req["status"]]


def test_submit_public_record_review_to_restricted_community(
    running_app, public_draft_review_restricted, service
):
    """Test creation of review after draft was created."""
    # Create draft
    with pytest.raises(ReviewInconsistentAccessRestrictions):
        req = service.review.submit(
            running_app.superuser_identity, public_draft_review_restricted.id
        ).to_dict()


def test_submit_restricted_record_review_to_restricted_community(
    running_app, restricted_draft_review_restricted, service
):
    """Test creation of review after draft was created."""
    # Create draft
    req = service.review.submit(
        running_app.superuser_identity, restricted_draft_review_restricted.id
    ).to_dict()
    assert req["status"] == "submitted"
    assert req["title"] == restricted_draft_review_restricted["metadata"]["title"]


def test_create_when_already_published(minimal_record, running_app, community, service):
    """Review creation should fail for published records."""
    # Create draft
    draft = service.create(running_app.superuser_identity, minimal_record)
    # Publish and edit the record.
    service.publish(running_app.superuser_identity, draft.id)
    draft = service.edit(running_app.superuser_identity, draft.id)
    # Then try to create a review (you use update, not create for this).
    data = {
        "type": "community-submission",
        "receiver": {"community": community.data["id"]},
    }
    with pytest.raises(ReviewStateError):
        service.review.update(
            running_app.superuser_identity,
            draft.id,
            data,
            revision_id=draft.data["revision_id"],
        )


def test_create_with_new_version(minimal_record, running_app, community, service):
    """Review creation should fail for unpublished new version."""
    # Create draft
    draft = service.create(running_app.superuser_identity, minimal_record)
    # Publish and create new version of the record.
    service.publish(running_app.superuser_identity, draft.id)
    draft = service.new_version(running_app.superuser_identity, draft.id)
    # Then try to create a review (you use update, not create for this).
    data = {
        "type": "community-submission",
        "receiver": {"community": community.data["id"]},
    }
    with pytest.raises(ReviewStateError):
        service.review.update(
            running_app.superuser_identity,
            draft.id,
            data,
            revision_id=draft.data["revision_id"],
        )


def test_update(draft, running_app, community2, service, db):
    """Change to a different community."""
    previous_id = draft.data["parent"]["review"]["id"]
    # Change to a different community
    data = {
        "type": "community-submission",
        "receiver": {"community": community2.data["id"]},
    }
    req = service.review.update(
        running_app.superuser_identity,
        draft.id,
        data,
        revision_id=draft.data["revision_id"],
    ).to_dict()
    assert req["id"] != previous_id
    assert req["status"] == "created"
    assert req["topic"] == {"record": draft.id}
    assert req["receiver"] == {"community": community2.data["id"]}


def test_publish_when_review_exists(draft, running_app, community, service):
    """Publish should fail if review exists."""
    with pytest.raises(ReviewExistsError):
        service.publish(running_app.superuser_identity, draft.id)


def test_delete(draft, running_app, service):
    """Test delete an open request."""
    # Delete the request
    res = service.review.delete(running_app.superuser_identity, draft.id)
    assert res is True

    # Review should not be found
    with pytest.raises(ReviewNotFoundError):
        service.review.read(running_app.superuser_identity, draft.id)


def test_delete_when_submitted(draft, running_app, service):
    """Test delete an open request."""
    service.review.submit(running_app.superuser_identity, draft.id)

    # Review is submitted (i.e. open) so not possible to delete.
    with pytest.raises(ReviewStateError):
        service.review.delete(running_app.superuser_identity, draft.id)


def test_delete_when_accepted(draft, running_app, service, requests_service):
    """Test delete an open request."""
    # Submit and accept
    service.review.submit(running_app.superuser_identity, draft.id)
    requests_service.execute_action(
        running_app.superuser_identity, draft["parent"]["review"]["id"], "accept", {}
    )

    # Review was already desassociated so nothing to delete.
    with pytest.raises(NoResultFound):
        service.review.delete(running_app.superuser_identity, draft.id)


def test_read_delete_submit_no_review(minimal_record, running_app, service):
    """Test when no review exists."""
    # Create draft without review
    draft = service.create(running_app.superuser_identity, minimal_record)

    # Read review
    with pytest.raises(ReviewNotFoundError):
        service.review.read(running_app.superuser_identity, draft.id)

    # Update is used for creation so not tested here

    # Delete review
    with pytest.raises(ReviewNotFoundError):
        service.review.delete(running_app.superuser_identity, draft.id)

    # Submit review
    with pytest.raises(ReviewNotFoundError):
        service.review.submit(running_app.superuser_identity, draft.id)


def test_delete_draft_unsubmitted(draft, running_app, service, requests_service):
    """Draft request should be deleted when the draft is deleted."""
    # Delete the draft
    req_id = draft.data["parent"]["review"]["id"]
    res = service.delete_draft(running_app.superuser_identity, draft.id)

    # Request was also deleted
    with pytest.raises(NoResultFound):
        requests_service.read(running_app.superuser_identity, req_id)


def test_delete_draft_when_submitted(draft, running_app, service):
    """Delete draft should fail when an open review exists."""
    service.review.submit(running_app.superuser_identity, draft.id).to_dict()

    # Delete the draft
    with pytest.raises(ReviewStateError):
        service.delete_draft(running_app.superuser_identity, draft.id)


def test_submit_with_validation_errors(running_app, community, service, minimal_record):
    """Fail to submit when draft has validation errors."""
    minimal_record["parent"] = {
        "review": {
            "type": "community-submission",
            "receiver": {"community": community.data["id"]},
        }
    }
    # Make a mistake in the record.
    del minimal_record["metadata"]["title"]
    # Create draft
    draft = service.create(running_app.superuser_identity, minimal_record)
    # Submit review - fails because of validation error
    with pytest.raises(ValidationError):
        service.review.submit(running_app.superuser_identity, draft.id)


def test_accept_with_validation_errors(draft, running_app, service, requests_service):
    # Submit review - fails because of validation error
    req = service.review.submit(running_app.superuser_identity, draft.id).to_dict()

    # Make a validation error change.
    draft = service.read_draft(running_app.superuser_identity, draft.id)
    data = draft.data
    del data["metadata"]["title"]
    service.update_draft(running_app.superuser_identity, draft.id, data)

    # Accept request
    pytest.raises(
        ValidationError,
        requests_service.execute_action,
        running_app.superuser_identity,
        req["id"],
        "accept",
        {},
    )


def test_review_gives_access_to_curator(running_app, draft, service, requests_service):
    """Test if a submission review request does give the curator access."""
    request_item = service.review.submit(running_app.superuser_identity, draft.id)
    request = request_item._request

    # the draft is the request's topic
    draft = request.topic.resolve()
    assert isinstance(draft, RDMDraft)

    # get the community from the request, and build the owner's identity
    community = request.receiver.resolve()
    assert isinstance(community, Community)
    identity = get_community_owner_identity(community)

    # the owner of the community should have access to the draft in question
    item = service.read_draft(identity, draft.pid.pid_value)
    assert item._record.id == draft.id

    # close the request
    request = requests_service.execute_action(
        running_app.superuser_identity, request.id, "cancel"
    )._request
    assert request.status == "cancelled"

    # the owner of the community should not have access anymore
    with pytest.raises(PermissionDeniedError):
        item = service.read_draft(identity, draft.pid.pid_value)


# TODO tests:
# - Test: submit to restricted community not allowed by user
#         (likely requires members structure in communities?)
# - Test: That another user cannot e.g. read reviews service.reviews.read
