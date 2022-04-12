# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Service level tests for Invenio RDM Records."""

import pytest
from invenio_requests import current_requests_service

from invenio_communities import current_communities
from invenio_communities.communities.records.api import Community
from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.services.errors import EmbargoNotLiftedError
from invenio_requests.customizations import RequestActions



@pytest.fixture()
def minimal_community2():
    """Data for a minimal community"""
    return {
        "id": "rdm",
        "access": {
            "visibility": "public",
        },
        "metadata": {
            "title": "Research Data Management",
            "type": "topic"
        }
    }


@pytest.fixture()
def community2(running_app, curator, minimal_community2):
    """Get the current RDM records service."""
    c = current_communities.service.create(
        curator.identity,
        minimal_community2,
    )
    Community.index.refresh()
    return c


@pytest.fixture()
def draft(minimal_record, community, service, running_app, db):
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


@pytest.fixture()
def draft2(minimal_record, community, community2, service, running_app, db):
    minimal_record['parent'] = {
        'review': {
            'type': 'community-submission',
            'receiver': {'community': community2.data['uuid']}
        },
        'communities': {
            'ids': [
                {'community': community2.data['uuid']},
                {'community': community.data['uuid']}
            ],
            'default': {'community': community2.data['uuid']}
        }
    }

    # Create draft with review
    return service.create(
        running_app.superuser_identity,
        minimal_record
    )


@pytest.fixture()
def service():
    """Get the current RDM records service."""
    return current_rdm_records.records_service


@pytest.fixture()
def requests_service():
    """Get the current RDM records service."""
    return current_requests_service


def test_minimal_draft_creation(running_app, es_clear, minimal_record):
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service

    record_item = service.create(superuser_identity, minimal_record)
    record_dict = record_item.to_dict()

    assert record_dict["metadata"]["resource_type"] == {
        'id': 'image-photo',
        'title': {'en': 'Photo'}
    }


def test_draft_w_languages_creation(running_app, es_clear, minimal_record):
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    minimal_record["metadata"]["languages"] = [{
        "id": "eng",
    }]

    record_item = service.create(superuser_identity, minimal_record)
    record_dict = record_item.to_dict()

    assert record_dict["metadata"]["languages"] == [{
        'id': 'eng',
        'title': {'en': 'English', 'da': 'Engelsk'}
    }]


#
# Embargo lift
#
def test_embargo_lift_without_draft(embargoed_record, running_app, es_clear):
    record = embargoed_record
    service = current_rdm_records.records_service

    service.lift_embargo(
        _id=record['id'],
        identity=running_app.superuser_identity
    )

    record_lifted = service.record_cls.pid.resolve(record['id'])
    assert record_lifted.access.embargo.active is False
    assert record_lifted.access.protection.files == 'public'
    assert record_lifted.access.protection.record == 'public'
    assert record_lifted.access.status.value == 'metadata-only'


def test_embargo_lift_with_draft(
        embargoed_record, es_clear, superuser_identity):
    record = embargoed_record
    service = current_rdm_records.records_service

    # Edit a draft
    ongoing_draft = service.edit(
        id_=record['id'], identity=superuser_identity)

    service.lift_embargo(_id=record['id'], identity=superuser_identity)
    record_lifted = service.record_cls.pid.resolve(record['id'])
    draft_lifted = service.draft_cls.pid.resolve(ongoing_draft['id'])

    assert record_lifted.access.embargo.active is False
    assert record_lifted.access.protection.files == 'public'
    assert record_lifted.access.protection.record == 'public'

    assert draft_lifted.access.embargo.active is False
    assert draft_lifted.access.protection.files == 'public'
    assert draft_lifted.access.protection.record == 'public'


def test_embargo_lift_with_updated_draft(
        embargoed_record, superuser_identity, es_clear):
    record = embargoed_record
    service = current_rdm_records.records_service

    # This draft simulates an existing one while lifting the record
    draft = service.edit(id_=record['id'], identity=superuser_identity).data

    # Change record's title and access field to be restricted
    draft["metadata"]["title"] = 'Record modified by the user'
    draft["access"]["status"] = 'restricted'
    draft["access"]["embargo"] = dict(
        active=False, until=None, reason=None
    )
    # Update the ongoing draft with the new data simulating the user's input
    ongoing_draft = service.update_draft(
        id_=draft['id'], identity=superuser_identity, data=draft)

    service.lift_embargo(_id=record['id'], identity=superuser_identity)
    record_lifted = service.record_cls.pid.resolve(record['id'])
    draft_lifted = service.draft_cls.pid.resolve(ongoing_draft['id'])

    assert record_lifted.access.embargo.active is False
    assert record_lifted.access.protection.files == 'public'
    assert record_lifted.access.protection.record == 'public'

    assert draft_lifted.access.embargo.active is False
    assert draft_lifted.access.protection.files == 'restricted'
    assert draft_lifted.access.protection.record == 'public'


def test_embargo_lift_with_error(running_app, es_clear, minimal_record):
    superuser_identity = running_app.superuser_identity
    service = current_rdm_records.records_service
    # Add embargo to record
    minimal_record["access"]["files"] = 'restricted'
    minimal_record["access"]["status"] = 'embargoed'
    minimal_record["access"]["embargo"] = dict(
        active=True, until='3220-06-01', reason=None
    )
    draft = service.create(superuser_identity, minimal_record)
    record = service.publish(id_=draft.id, identity=superuser_identity)

    # Record should not be lifted since it didn't expire (until 3220)
    with pytest.raises(EmbargoNotLiftedError):
        service.lift_embargo(_id=record['id'], identity=superuser_identity)


def test_search_community_records(draft, running_app, community, service,
                                  requests_service):
    req = service.review.submit(
        running_app.superuser_identity, draft.id).to_dict()
    req = requests_service.execute_action(
        running_app.superuser_identity,
        req['id'],
        'accept',
        {}
    ).to_dict()

    RDMRecord.index.refresh()

    records = service.search_community_records(
        running_app.superuser_identity,
        community_uuid=community.to_dict()['uuid'],
    )

    assert records.to_dict()["hits"]["total"] == 1

def test_search_community_records2(draft, running_app, community, service,
                                  requests_service, db):
    draft = draft._record
    draft.parent.communities.add(community, request=None, default=True)
    draft.parent.commit()
    service.publish(running_app.superuser_identity, draft.pid.pid_value)
    RDMRecord.index.refresh()

    records = service.search_community_records(
        running_app.superuser_identity,
        community_uuid=community.to_dict()['uuid'],
    )

    assert records.to_dict()["hits"]["total"] == 1


def test_search_community_records_multiple(draft, draft2, running_app, community, service,
                                  requests_service):

    data = {
        "parent": {
            "communities": {
                "ids": {}
            }
        }
    }
    data['parent']['communities']['ids'] = {
        'community': community.data['uuid']
    }

    req = service.review.submit(
        running_app.superuser_identity, draft.id).to_dict()
    req = requests_service.execute_action(
        running_app.superuser_identity,
        req['id'],
        'accept',
        {}
    ).to_dict()

    req = service.review.submit(
        running_app.superuser_identity, draft2.id).to_dict()

    service.update_draft(
        running_app.superuser_identity,
        draft2.id,
        data
    )

    RDMRecord.index.refresh()

    records = service.search_community_records(
        running_app.superuser_identity,
        community_uuid=community.to_dict()['uuid'],
    )

    assert records.to_dict()["hits"]["total"] == 2
