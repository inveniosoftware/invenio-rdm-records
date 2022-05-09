# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
# Copyright (C) 2021-2022 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks for fixtures."""

import random

from celery import shared_task
from flask import current_app
from flask_principal import Identity, UserNeed
from invenio_access.permissions import any_user, authenticated_user, \
    system_identity
from invenio_communities.generators import CommunityRoleNeed
from invenio_communities.members.errors import AlreadyMemberError
from invenio_communities.members.records.api import Member
from invenio_communities.proxies import current_communities
from invenio_records_resources.proxies import current_service_registry
from invenio_requests import current_events_service, current_requests_service
from invenio_requests.customizations import CommentEventType

from ..proxies import current_rdm_records_service
from ..requests import CommunitySubmission
from ..services.errors import ReviewNotFoundError
from .demo import create_fake_comment


def get_authenticated_identity(user_id):
    """Return an authenticated identity for the given user."""
    identity = Identity(user_id)
    identity.provides.add(any_user)
    identity.provides.add(UserNeed(user_id))
    identity.provides.add(authenticated_user)
    return identity


@shared_task
def create_vocabulary_record(service_str, data):
    """Create a vocabulary record."""
    service = current_service_registry.get(service_str)
    service.create(system_identity, data)


@shared_task
def create_demo_record(user_id, data, publish=True):
    """Create demo record."""
    service = current_rdm_records_service
    identity = get_authenticated_identity(user_id)
    identity.provides.add(UserNeed(user_id))

    draft = service.create(data=data, identity=identity)
    if publish:
        service.publish(id_=draft.id, identity=identity)


@shared_task
def create_demo_community(user_id, data):
    """Create demo community."""
    identity = get_authenticated_identity(user_id)
    current_communities.service.create(identity, data)


def _get_random_community(communities):
    """Get random community."""
    r = random.randint(0, len(communities) - 1)
    id = communities[r]["id"]
    # create community owner identity
    members = current_communities.service.members
    Member.index.refresh()
    res = members.search(system_identity, id, role="owner").to_dict()
    owner_id = int(res['hits']['hits'][0]['member']['id'])
    owner_identity = get_authenticated_identity(owner_id)
    owner_identity.provides.add(CommunityRoleNeed(id, 'owner'))
    return id, owner_id, owner_identity


def _add_comments_to_request(request, user_identity, comm_identity):
    """Add a random number of comments to the request."""
    for _ in range(random.randint(0, 9)):
        identity = random.choice([user_identity, comm_identity])
        comment = create_fake_comment()
        current_events_service.create(
            identity, request.id, comment, CommentEventType)


@shared_task
def create_demo_inclusion_requests(user_id, n_requests):
    """Create requests to include drafts to communities."""
    review_service = current_rdm_records_service.review
    comm_results = current_communities.service.search(system_identity)
    communities = comm_results.to_dict()["hits"]["hits"]

    user_identity = get_authenticated_identity(user_id)
    results = current_rdm_records_service.search_drafts(user_identity,
                                                        is_published=False,
                                                        q="versions.index:1")
    drafts = results.to_dict()["hits"]["hits"]

    for _ in range(n_requests):
        community_id, _, comm_owner_identity = \
            _get_random_community(communities)

        # get a random draft
        r = random.randint(0, len(drafts)-1)
        draft_id = drafts[r]["id"]

        # create the request in `draft` state and update the draft record
        # with the `community-submission` review in the parent
        data = {
            "type": CommunitySubmission.type_id,
            "receiver": {"community": community_id}
        }

        # ensure this draft does not have a review yet
        try:
            review_service.read(user_identity, draft_id)
        except ReviewNotFoundError:
            pass
        else:
            # did not raise, it has already a review
            continue

        review_service.update(user_identity, draft_id, data)
        req = review_service.submit(user_identity, draft_id)
        _add_comments_to_request(req, user_identity, comm_owner_identity)

        # Randomly set if the request should be open, or an action happened
        _action, _identity = random.choice([
            (None, None),
            ("cancel", user_identity),
            ("accept", comm_owner_identity),
            ("decline", comm_owner_identity),
            ("expire", system_identity)
        ])
        if _action:
            comment = create_fake_comment()
            current_requests_service.execute_action(
                _identity,
                req.id,
                _action,
                comment
            )

        print(f"Created request {req.id} and action {_action} "
              f"for community {community_id}")


@shared_task
def create_demo_invitation_requests(user_id, n_requests):
    """Create requests to invite a user to a community."""
    user_identity = get_authenticated_identity(user_id)
    comm_results = current_communities.service.search(user_identity)
    communities = comm_results.to_dict()["hits"]["hits"]
    role_names = current_app.config["COMMUNITIES_ROLES"]

    for _ in range(n_requests):
        community_id, _, _ = _get_random_community(communities)
        random_role = random.choice(role_names)
        invitation_data = {
            "members": [
                {
                    "type": "user",
                    "id": str(user_id),
                }
            ],
            "role": random_role["name"],
            "visible": True,
        }

        try:
            current_communities.service.members.invite(
                system_identity, community_id, invitation_data
            )
        except AlreadyMemberError:
            continue

        # # Randomly set if the request should be open, or an action happened
        # # only "accept" action implemented at this moment
        # _action, _identity = random.choice([
        #     (None, None),
        #     ("cancel", user_identity),
        #     ("accept", comm_owner_identity),
        #     ("decline", comm_owner_identity),
        #     ("expire", system_identity)
        # ])
        # if _action:
        #     _, comment_with_type = create_fake_comment()
        #     current_requests_service.execute_action(
        #         _identity,
        #         req.id,
        #         _action,
        #         comment_with_type
        #     )

        print(f"Created request for user {user_id} and "
              f"community {community_id}")
