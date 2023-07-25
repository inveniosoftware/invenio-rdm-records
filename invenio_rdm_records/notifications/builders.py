# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Notification related utils for notifications."""

from invenio_communities.notifications.generators import CommunityMembersRecipient
from invenio_notifications.models import Notification
from invenio_notifications.registry import EntityResolverRegistry
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.generators import EntityResolve, UserEmailBackend
from invenio_requests.notifications.filters import UserRecipientFilter
from invenio_users_resources.notifications.filters import UserPreferencesRecipientFilter


class CommunityInclusionNotificationBuilder(NotificationBuilder):
    """Base notification builder for record community inclusion events."""

    type = "community-submission"

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
    ]

    recipient_filters = [
        UserPreferencesRecipientFilter(),
        UserRecipientFilter(key="request.created_by"),
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]


class CommunityInclusionSubmittedNotificationBuilder(
    CommunityInclusionNotificationBuilder
):
    """Notification builder for record community inclusion submitted."""

    type = "community-submission.submit"
