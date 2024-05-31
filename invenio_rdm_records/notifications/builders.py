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
from invenio_users_resources.notifications.generators import (
    EmailRecipient,
    IfUserRecipient,
    UserRecipient,
)


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
        CommunityMembersRecipient(
            key="request.receiver", roles=["curator", "owner", "manager"]
        ),
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


class GuestAccessRequestTokenCreateNotificationBuilder(NotificationBuilder):
    """Notification builder for user access requests."""

    type = "guest-access-request-token.create"

    @classmethod
    def build(cls, record, email, verify_url):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "record": EntityResolverRegistry.reference_entity(record),
                "created_by": EntityResolverRegistry.reference_entity(email),
                "verify_url": verify_url,
            },
        )

    context = [
        EntityResolve(key="record"),
        EntityResolve(key="created_by"),  # email
    ]

    recipients = [
        EmailRecipient(key="created_by"),  # email only
    ]

    recipient_filters = []  # assume guest is ok with mail being sent

    recipient_backends = [
        UserEmailBackend(),
    ]


class GuestAccessRequestDeclineNotificationBuilder(NotificationBuilder):
    """Notification builder for user access requests."""

    type = "guest-access-request.decline"

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
        EntityResolve(key="request.created_by"),  # email
        EntityResolve(key="request.topic"),
    ]

    recipients = [
        EmailRecipient(key="request.created_by"),  # email only
    ]

    recipient_filters = []  # assume guest is ok with mail being sent

    recipient_backends = [
        UserEmailBackend(),
    ]


class GuestAccessRequestCancelNotificationBuilder(NotificationBuilder):
    """Notification builder for user access requests."""

    type = "guest-access-request.cancel"

    @classmethod
    def build(cls, request, identity):
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
        EmailRecipient(key="request.created_by"),  # email only
    ]

    recipient_filters = []

    recipient_backends = [
        UserEmailBackend(),
    ]


class GuestAccessRequestSubmittedNotificationBuilder(NotificationBuilder):
    """Notification builder for submitted guest access requests."""

    type = "guest-access-request.submitted"

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
    ]

    recipients = [
        EmailRecipient(key="request.created_by"),
    ]

    recipient_filters = [
        UserPreferencesRecipientFilter(),
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]


class GuestAccessRequestSubmitNotificationBuilder(NotificationBuilder):
    """Notification builder for guest access requests."""

    type = "guest-access-request.submit"

    @classmethod
    def build(cls, request):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
                "receiver_entity": request.receiver.reference_dict,  # will not be resolved for easier lookup for recipients
            },
        )

    context = [
        EntityResolve(key="request"),
        EntityResolve(key="request.created_by"),
        EntityResolve(key="request.topic"),
        EntityResolve(key="request.receiver"),
    ]

    recipients = [
        # Currently only these two are allowed. Adapt as needed.
        IfUserRecipient(
            key="receiver_entity",
            then_=[UserRecipient(key="request.receiver")],
            else_=[
                CommunityMembersRecipient(
                    key="request.receiver", roles=["curator", "owner"]
                )
            ],
        )
    ]

    recipient_filters = [
        UserPreferencesRecipientFilter(),
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]


class GuestAccessRequestAcceptNotificationBuilder(NotificationBuilder):
    """Notification builder for user access requests."""

    type = "guest-access-request.accept"

    @classmethod
    def build(cls, request, access_url):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
                "access_url": access_url,
            },
        )

    context = [
        EntityResolve(key="request"),
        EntityResolve(key="request.created_by"),  # email
        EntityResolve(key="request.topic"),
    ]

    recipients = [
        EmailRecipient(key="request.created_by"),  # email only
    ]

    recipient_filters = []  # assume guest is ok with mail being sent

    recipient_backends = [
        UserEmailBackend(),
    ]


class UserAccessRequestDeclineNotificationBuilder(NotificationBuilder):
    """Notification builder for user access requests."""

    type = "user-access-request.decline"

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
        UserRecipient(key="request.created_by"),
    ]

    recipient_filters = [
        UserPreferencesRecipientFilter(),
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]


class UserAccessRequestCancelNotificationBuilder(NotificationBuilder):
    """Notification builder for user access requests."""

    type = "user-access-request.cancel"

    @classmethod
    def build(cls, request, identity):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
                "executing_user": EntityResolverRegistry.reference_identity(identity),
            },
        )

    context = [
        EntityResolve(key="request"),
        EntityResolve(key="request.created_by"),
        EntityResolve(key="request.topic"),
        EntityResolve(key="request.receiver"),
        EntityResolve(key="executing_user"),
    ]

    recipients = [
        UserRecipient(key="request.created_by"),
    ]

    recipient_filters = [
        UserPreferencesRecipientFilter(),
        UserRecipientFilter("executing_user"),
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]


class UserAccessRequestSubmitNotificationBuilder(NotificationBuilder):
    """Notification builder for user access requests."""

    type = "user-access-request.submit"

    @classmethod
    def build(cls, request):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
                "receiver_entity": request.receiver.reference_dict,  # will not be resolved for easier lookup for recipients
            },
        )

    context = [
        EntityResolve(key="request"),
        EntityResolve(key="request.created_by"),
        EntityResolve(key="request.topic"),
        EntityResolve(key="request.receiver"),
    ]

    recipients = [
        # Currently only these two are allowed. Adapt as needed.
        IfUserRecipient(
            key="receiver_entity",
            then_=[UserRecipient(key="request.receiver")],
            else_=[
                CommunityMembersRecipient(
                    key="request.receiver", roles=["curator", "owner"]
                )
            ],
        )
    ]

    recipient_filters = [
        UserPreferencesRecipientFilter(),
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]


class UserAccessRequestAcceptNotificationBuilder(NotificationBuilder):
    """Notification builder for user access requests."""

    type = "user-access-request.accept"

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
        UserRecipient(key="request.created_by"),
    ]

    recipient_filters = [
        UserPreferencesRecipientFilter(),
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]


class GrantUserAccessNotificationBuilder(NotificationBuilder):
    """Notification builder for user access grant."""

    type = "grant-user-access.create"

    @classmethod
    def build(cls, record, user, permission, message=None):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "record": EntityResolverRegistry.reference_entity(record),
                "receiver": EntityResolverRegistry.reference_entity(user),
                "permission": permission,
                "message": message,
            },
        )

    context = [
        EntityResolve(key="record"),
        EntityResolve(key="receiver"),
    ]

    recipients = [
        UserRecipient(key="receiver"),
    ]

    recipient_filters = [
        UserPreferencesRecipientFilter(),
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]


class CommunityInclusionActionNotificationBuilder(NotificationBuilder):
    """Notification builder for inclusion actions."""

    @classmethod
    def build(cls, identity, request):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
                "executing_user": EntityResolverRegistry.reference_identity(identity),
            },
        )

    context = [
        EntityResolve(key="request"),
        EntityResolve(key="request.created_by"),
        EntityResolve(key="request.topic"),
        EntityResolve(key="request.receiver"),
        EntityResolve(key="executing_user"),
    ]

    recipients = [
        UserRecipient("request.created_by"),
    ]

    recipient_filters = [
        UserPreferencesRecipientFilter(),
        UserRecipientFilter("executing_user"),
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]


class CommunityInclusionAcceptNotificationBuilder(
    CommunityInclusionActionNotificationBuilder
):
    """Notification builder for inclusion accept action."""

    type = f"{CommunityInclusionNotificationBuilder.type}.accept"


class CommunityInclusionAcceptNotificationBuilder(
    CommunityInclusionActionNotificationBuilder
):
    """Notification builder for inclusion accept action."""

    type = f"{CommunityInclusionNotificationBuilder.type}.accept"


class CommunityInclusionCancelNotificationBuilder(
    CommunityInclusionActionNotificationBuilder
):
    """Notification builder for inclusion cancel action."""

    type = f"{CommunityInclusionNotificationBuilder.type}.cancel"

    recipients = [
        CommunityMembersRecipient("request.receiver", roles=["curator", "owner"]),
    ]


class CommunityInclusionDeclineNotificationBuilder(
    CommunityInclusionActionNotificationBuilder
):
    """Notification builder for inclusion decline action."""

    type = f"{CommunityInclusionNotificationBuilder.type}.decline"


class CommunityInclusionExpireNotificationBuilder(
    CommunityInclusionActionNotificationBuilder
):
    """Notification builder for inclusion expire action."""

    type = f"{CommunityInclusionNotificationBuilder.type}.expire"

    # Executing user will most probably be the system. It is not resolvable on the service level
    # as of now and we do not use it in the template.
    context = [
        EntityResolve(key="request"),
        EntityResolve(key="request.created_by"),
        EntityResolve(key="request.topic"),
        EntityResolve(key="request.receiver"),
    ]
