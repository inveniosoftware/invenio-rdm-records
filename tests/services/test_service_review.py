# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test of the review deposit integration."""

import pytest
from invenio_communities import current_communities
from invenio_requests import current_requests_service
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm.exc import NoResultFound

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.services.errors import ReviewExistsError, \
    ReviewNotFoundError, ReviewStateError


@pytest.fixture()
def service():
    """Get the current RDM records service."""
    return current_rdm_records.records_service


@pytest.fixture()
def requests_service():
    """Get the current RDM records service."""
    return current_requests_service


@pytest.fixture()
def minimal_community():
    """Data for a minimal community"""
    return {
        "id": "blr",
        "access": {
            "visibility": "public",
        },
        "metadata": {
            "title": "Biodiversity Literature Repository",
            "type": "topic"
        }
    }


@pytest.fixture()
def minimal_community2():
    """Data for a minimal community"""
    return {
        "id": "rdm",
        "access": {
            "visibility": "public",
        },
        "metadata": {
            "title": "RDM",
            "type": "topic"
        }
    }


@pytest.fixture()
def community(running_app, minimal_community):
    """Get the current RDM records service."""
    return current_communities.service.create(
        running_app.superuser_identity,
        minimal_community,
    )


@pytest.fixture()
def community2(running_app, minimal_community2):
    """Get the current RDM records service."""
    return current_communities.service.create(
        running_app.superuser_identity,
        minimal_community2,
    )


@pytest.fixture()
def draft(minimal_record, community, service, running_app):
    minimal_record['parent'] = {
        'review': {
            'type': 'community-submission',
            'receiver': {'community': community.data['uuid']}
        }
    }

    # Create draft with review
    return service.create(
        running_app.superuser_identity,
        minimal_record
    )


#
# Tests
#
def test_simple_flow(draft, running_app, community, service,
                     requests_service):
    """Test basic creation with review."""
    # ### Submit draft for review
    req = service.review.submit(
        draft.id, running_app.superuser_identity).to_dict()
    assert req['status'] == 'open'
    assert req['title'] == draft['metadata']['title']

    # ### Read request as curator
    # TODO: test that curator can search/read the request
    # TODO: check links - curator should not see cancel link

    # ### Accept request
    req = requests_service.execute_action(
        running_app.superuser_identity,
        req['id'],
        'accept',
        {}
    ).to_dict()
    assert req['status'] == 'accepted'
    assert req['is_open'] is False

    # ### Read the record
    record = service.read(draft.id, running_app.superuser_identity).to_dict()
    assert 'review' not in record["parent"]  # Review was desassociated
    assert record["is_published"] is True
    assert record['parent']['communities']['ids'] == [community.data['uuid']]
    assert record['parent']['communities']['default'] == community.data['uuid']

    # ### Read draft (which should have been removed)
    pytest.raises(
        NoResultFound,
        service.read_draft,
        draft.id,
        running_app.superuser_identity
    )

    # ### Create a new version (still part of community)
    draft = service.new_version(
        draft.id, running_app.superuser_identity).to_dict()
    assert 'review' not in draft['parent']
    assert draft['parent']['communities']['ids'] == [community.data['uuid']]
    assert draft['parent']['communities']['default'] == community.data['uuid']


def test_creation(draft, running_app, community, service, requests_service):
    """Test basic creation with review."""
    # See the draft fixture for the actual creation
    record_id = draft.id
    parent = draft.to_dict()['parent']

    assert 'id' in parent['review']
    assert parent['review']['type'] == 'community-submission'
    assert parent['review']['receiver'] == {
        'community': community.data['uuid']}
    assert '@v' not in parent['review']  # internals should not be exposed

    # Read review request (via request service)
    review = requests_service.read(
        parent['review']['id'], running_app.superuser_identity
    ).to_dict()

    assert review['id'] == parent['review']['id']
    assert review['status'] == 'draft'
    assert review['type'] == 'community-submission'
    assert review['receiver'] == {'community': community.data['uuid']}
    assert review['created_by'] == {
        'user': str(running_app.superuser_identity.id)
    }
    assert review['topic'] == {'record': record_id}

    # Read review request (via record review subservice)
    review = service.review.read(
        record_id,
        running_app.superuser_identity
    ).to_dict()
    assert review['id'] == parent['review']['id']

    # TODO: Test that curator cannot see it yet


def test_create_with_invalid_community(minimal_record, running_app, service):
    """Test with invalid communities"""
    minimal_record['parent'] = {
        'review': {
            'type': 'community-submission',
            'receiver': {'community': '00000000-0000-0000-0000-000000000000'}
        }
    }
    pytest.raises(
        NoResultFound,
        service.create,
        running_app.superuser_identity,
        minimal_record,
    )

    minimal_record['parent'] = {
        'review': {
            'type': 'community-submission',
            'receiver': {'community': 'invalid'}
        }
    }
    pytest.raises(
        NoResultFound,
        service.create,
        running_app.superuser_identity,
        minimal_record,
    )


def test_create_review_after_draft(
        running_app, community, service, minimal_record):
    """Test creation of review after draft was created."""
    # Create draft
    draft = service.create(running_app.superuser_identity, minimal_record)
    # Then create review (you use update, not create for this).
    data = {
        'type': 'community-submission',
        'receiver': {'community': community.data['uuid']}
    }
    req = service.review.update(
        draft.id,
        running_app.superuser_identity,
        data,
        revision_id=draft.data['revision_id']
    ).to_dict()
    assert req['status'] == 'draft'
    assert req['topic'] == {'record': draft.id}
    assert req['receiver'] == {'community': community.data['uuid']}


def test_create_when_already_published(
        minimal_record, running_app, community, service):
    """Review creation should fail for published records."""
    # Create draft
    draft = service.create(running_app.superuser_identity, minimal_record)
    # Publish and edit the record.
    service.publish(draft.id, running_app.superuser_identity)
    draft = service.edit(draft.id, running_app.superuser_identity)
    # Then try to create a review (you use update, not create for this).
    data = {
        'type': 'community-submission',
        'receiver': {'community': community.data['uuid']}
    }
    pytest.raises(
        ReviewStateError,
        service.review.update,
        draft.id,
        running_app.superuser_identity,
        data,
        revision_id=draft.data['revision_id']
    )


def test_create_with_new_version(
        minimal_record, running_app, community, service):
    """Review creation should fail for unpublished new version."""
    # Create draft
    draft = service.create(running_app.superuser_identity, minimal_record)
    # Publish and create new version of the record.
    service.publish(draft.id, running_app.superuser_identity)
    draft = service.new_version(draft.id, running_app.superuser_identity)
    # Then try to create a review (you use update, not create for this).
    data = {
        'type': 'community-submission',
        'receiver': {'community': community.data['uuid']}
    }
    pytest.raises(
        ReviewStateError,
        service.review.update,
        draft.id,
        running_app.superuser_identity,
        data,
        revision_id=draft.data['revision_id']
    )


def test_update(draft, running_app, community2, service):
    """Change to a different community."""
    previous_id = draft.data['parent']['review']['id']
    # Change to a different community
    data = {
        'type': 'community-submission',
        'receiver': {'community': community2.data['uuid']}
    }
    req = service.review.update(
        draft.id,
        running_app.superuser_identity,
        data,
        revision_id=draft.data['revision_id']
    ).to_dict()
    assert req['id'] != previous_id
    assert req['status'] == 'draft'
    assert req['topic'] == {'record': draft.id}
    assert req['receiver'] == {'community': community2.data['uuid']}


def test_publish_when_review_exists(draft, running_app, community, service):
    """Publish should fail if review exists."""
    pytest.raises(
        ReviewExistsError,
        service.publish,
        draft.id,
        running_app.superuser_identity,
    )


def test_delete(draft, running_app, service):
    """Test delete an open request."""
    # Delete the request
    res = service.review.delete(draft.id, running_app.superuser_identity)
    assert res is True

    # Review should not be found
    pytest.raises(
        ReviewNotFoundError,
        service.review.read,
        draft.id,
        running_app.superuser_identity
    )


def test_delete_when_submitted(draft, running_app, service):
    """Test delete an open request."""
    service.review.submit(draft.id, running_app.superuser_identity)

    # Review is submitted (i.e. open) so not possible to delete.
    pytest.raises(
        ReviewStateError,
        service.review.delete,
        draft.id,
        running_app.superuser_identity
    )


def test_delete_when_accepted(draft, running_app, service, requests_service):
    """Test delete an open request."""
    # Submit and accept
    service.review.submit(draft.id, running_app.superuser_identity)
    requests_service.execute_action(
        running_app.superuser_identity,
        draft['parent']['review']['id'],
        'accept',
        {}
    )

    # Review was already desassociated so nothing to delete.
    pytest.raises(
        NoResultFound,
        service.review.delete,
        draft.id,
        running_app.superuser_identity
    )


def test_read_delete_submit_no_review(minimal_record, running_app, service):
    """Test when no review exists."""
    # Create draft without review
    draft = service.create(
        running_app.superuser_identity,
        minimal_record
    )

    # Read review
    pytest.raises(
        ReviewNotFoundError,
        service.review.read,
        draft.id,
        running_app.superuser_identity
    )

    # Update is used for creation so not tested here

    # Delete review
    pytest.raises(
        ReviewNotFoundError,
        service.review.delete,
        draft.id,
        running_app.superuser_identity
    )

    # Submit review
    pytest.raises(
        ReviewNotFoundError,
        service.review.submit,
        draft.id,
        running_app.superuser_identity
    )


def test_delete_draft_unsubmitted(
        draft, running_app, service, requests_service):
    """Draft request should be deleted when the draft is deleted."""
    # Delete the draft
    req_id = draft.data['parent']['review']['id']
    res = service.delete_draft(draft.id, running_app.superuser_identity)

    # Request was also deleted
    pytest.raises(
        NoResultFound,
        requests_service.read,
        req_id,
        running_app.superuser_identity
    )


def test_delete_draft_when_submitted(
        draft, running_app, service):
    """Delete draft should fail when an open review exists."""
    service.review.submit(draft.id, running_app.superuser_identity).to_dict()

    # Delete the draft
    pytest.raises(
        ReviewStateError,
        service.delete_draft,
        draft.id,
        running_app.superuser_identity
    )


def test_submit_with_validation_errors(
        running_app, community, service, minimal_record):
    """Fail to submit when draft has validation errors."""
    minimal_record['parent'] = {
        'review': {
            'type': 'community-submission',
            'receiver': {'community': community.data['uuid']}
        }
    }
    # Make a mistake in the record.
    del minimal_record['metadata']['title']
    # Create draft
    draft = service.create(running_app.superuser_identity, minimal_record)
    # Submit review - fails because of validation error
    pytest.raises(
        ValidationError,
        service.review.submit,
        draft.id,
        running_app.superuser_identity,
    )


def test_accept_with_validation_errors(
        draft, running_app, service, requests_service):
    # Submit review - fails because of validation error
    req = service.review.submit(
        draft.id, running_app.superuser_identity).to_dict()

    # Make a validation error change.
    draft = service.read_draft(draft.id, running_app.superuser_identity)
    data = draft.data
    del data['metadata']['title']
    service.update_draft(draft.id, running_app.superuser_identity, data)

    # Accept request
    pytest.raises(
        ValidationError,
        requests_service.execute_action,
        running_app.superuser_identity,
        req['id'],
        'accept',
        {}
    )


# TODO tests:
# - Test submit to restricted community not allowed by user
# - Test: That another user cannot e.g. read reviews service.reviews.read
