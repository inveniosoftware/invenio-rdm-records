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

from invenio_rdm_records.proxies import current_rdm_records


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
def community(running_app, minimal_community):
    """Get the current RDM records service."""
    return current_communities.service.create(
        running_app.superuser_identity,
        minimal_community,
    )


def test_creation(running_app, community, minimal_record, service,
                  requests_service):
    """Test basic creation with review."""

    minimal_record['parent'] = {
        'review': {
            'type': 'community-submission',
            'receiver': {'community': community.data['uuid']}
        }
    }

    # Create draft review
    data = service.create(
        running_app.superuser_identity,
        minimal_record
    )
    record_id = data.id
    parent = data.to_dict()['parent']

    assert 'id' in parent['review']
    assert parent['review']['type'] == 'community-submission'
    assert parent['review']['receiver'] == {'community': community.data['uuid']}

    # Read review request
    review = requests_service.read(
        parent['review']['id'], running_app.superuser_identity
    ).to_dict()

    assert review['id'] == parent['review']['id']
    assert review['type'] == 'community-submission'
    assert review['receiver'] == {'community': community.data['uuid']}
    assert review['created_by'] == {
        'user': str(running_app.superuser_identity.id)
    }
    assert review['topic'] == {'record': record_id}

    review = service.review.read(
        record_id,
        running_app.superuser_identity
    ).to_dict()
    assert review['id'] == parent['review']['id']



def test_simple_flow(running_app, community, minimal_record, service,
                     requests_service):
    """Test basic creation with review."""
    # Create draft review
    minimal_record['parent'] = {
        'review': {
            'type': 'community-submission',
            'receiver': {'community': community.id}
        }
    }

    data = service.create(
        running_app.superuser_identity,
        minimal_record
    ).to_dict()
    rec_id = data['id']

    review = data['parent']['review']
    # assert review['request_type'] == 'community-submission'
    # assert review['receiver'] == {'community': 'blr'}
    # assert review['created_by'] == {
    #    'user': running_app.superuser_identity.get_id()
    # }
    # assert review['topic'] == {'record': data['id']}

    data = service.review.submit(
        rec_id,
        running_app.superuser_identity,
    ).to_dict()

    data = requests_service.execute_action(
        running_app.superuser_identity,
        review['id'],
        'accept',
        {}
    ).to_dict()

    data = service.read(
        rec_id,
        running_app.superuser_identity,
    ).to_dict()

    assert len(data['parent']['communities']['ids']) == 1


# TODO tests:
# - review should only be readable by curators, not previewers and viewers.
# - only specific receivers should be allowed - should action run a
#   RequestType.is_valid_receiver() - who validates what's a valid receiver?
# - validate that only valid request types can be used (should be more
#   constrained than all request types)
