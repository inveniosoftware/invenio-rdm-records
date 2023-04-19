# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Notification related utils for notifications."""

from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_notifications.models import Notification, Recipient
from invenio_notifications.registry import EntityResolverRegistry
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.generators import EntityResolve
from invenio_records.dictutils import dict_lookup
from invenio_users_resources.notifications import UserEmailBackend, UserRecipient
from invenio_users_resources.proxies import current_users_service

from .events import CommunityInclusionSubmittedEvent


# TODO: move to invenio-communities?
class CommunityMembersRecipient:
    """Community member recipient generator for notifications."""

    def __init__(self, key, roles=None):
        """Ctor."""
        self.key = key
        self.roles = roles

    def __call__(self, notification, recipients: dict):
        """Fetch community and add members as recipients, based on roles."""
        community = dict_lookup(notification.context, self.key)
        members = current_communities.service.members.search(
            system_identity,
            community["id"],
            roles=self.roles,
        )

        user_ids = []
        for m in members:
            if m["member"]["type"] != "user":
                continue
            if self.roles and m["role"] not in self.roles:
                continue
            user_ids.append(m["member"]["id"])

        if not user_ids:
            return recipients

        users = current_users_service.read_many(system_identity, user_ids)
        for u in users:
            # NOTE: Community preferences are under construction See https://github.com/inveniosoftware/invenio-communities/issues/864
            #       Might want to move this to a RecipientFilter?
            # notif_pref = user.preferences.get("notifications", {})
            # com_pref = notif_pref.get(community.id, {})
            # if not com_pref.get("enabled"):
            #     continue
            recipients[u["id"]] = Recipient(data=u)
        return recipients


class CommunityInclusionNotificationBuilder(NotificationBuilder):
    """Base notification builder for record community inclusion events."""

    type = CommunityInclusionSubmittedEvent.handling_key

    @classmethod
    def build(cls, request):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
            },
        )

    context = [
        EntityResolve(key="request"),
        EntityResolve(key="request.created_by"),
        EntityResolve(key="request.topic"),
        EntityResolve(key="request.receiver"),
    ]

    recipients = [
        CommunityMembersRecipient(key="request.receiver", roles=["curator", "owner"]),
        UserRecipient(key="request.created_by"),
    ]

    recipient_filters = []

    recipient_backends = [
        UserEmailBackend(),
    ]


class CommunityInclusionSubmittedNotificationBuilder(
    CommunityInclusionNotificationBuilder
):
    """Notification builder for record community inclusion submitted."""

    type = CommunityInclusionSubmittedEvent.handling_key
