# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""
Notification builders for VCS.

These are kept in a separate file as invenio-vcs is an optional dependency, so imports would fail if the package isn't available.
"""

from invenio_notifications.models import Notification
from invenio_notifications.registry import EntityResolverRegistry
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.generators import EntityResolve, UserEmailBackend
from invenio_users_resources.notifications.filters import UserPreferencesRecipientFilter
from invenio_vcs.generic_models import GenericRelease, GenericRepository
from invenio_vcs.notifications.generators import RepositoryUsersRecipient


class RepositoryReleaseNotificationBuilder(NotificationBuilder):
    """Notification builder for repository release events."""

    type = "repository-release"

    @classmethod
    def build(
        cls,
        provider: str,
        generic_repository: GenericRepository,
        generic_release: GenericRelease,
    ):
        """Build the notification."""
        return Notification(
            type=cls.type,
            context={
                "provider": provider,
                "repository_provider_id": generic_repository.id,
                "repository_full_name": generic_repository.full_name,
                "release_tag": generic_release.tag_name,
            },
        )

    context = []

    recipients = [RepositoryUsersRecipient("provider", "repository_provider_id")]

    recipient_filters = [UserPreferencesRecipientFilter()]

    recipient_backends = [UserEmailBackend()]


class RepositoryReleaseSuccessNotificationBuilder(RepositoryReleaseNotificationBuilder):
    """Notification builder for successful repository release events."""

    type = f"{RepositoryReleaseNotificationBuilder.type}.success"

    @classmethod
    def build(
        cls,
        provider: str,
        generic_repository: GenericRepository,
        generic_release: GenericRelease,
        record,
        warnings: list[str],
    ):
        """Build the notification."""
        notification = super().build(provider, generic_repository, generic_release)
        notification.context["record"] = EntityResolverRegistry.reference_entity(record)
        notification.context["warnings"] = warnings
        return notification

    context = [EntityResolve(key="record")]


class RepositoryReleaseFailureNotificationBuilder(RepositoryReleaseNotificationBuilder):
    """
    Notification builder for failed repository release events.

    The failure might occur before or after a draft has been successfully saved, so `draft` is allowed
    to be `None`. The notification message should include a link to edit the draft if it's available.
    """

    type = f"{RepositoryReleaseNotificationBuilder.type}.failure"

    @classmethod
    def build(
        cls,
        provider: str,
        generic_repository: GenericRepository,
        generic_release: GenericRelease,
        error_message: str,
        draft=None,
    ):
        """Build the notification."""
        notification = super().build(provider, generic_repository, generic_release)
        notification.context["error_message"] = error_message
        if draft is not None:
            notification.context["draft"] = EntityResolverRegistry.reference_entity(
                draft
            )
        else:
            notification.context["draft"] = None
        return notification

    context = [EntityResolve(key="draft")]


class RepositoryReleaseCommunityRequiredNotificationBuilder(
    RepositoryReleaseNotificationBuilder
):
    """
    Release is saved as a draft but the user needs to add a community.

    Notification builder for when a release is saved as a draft but
    fails to be published because the user needs to manually select
    a community for the draft.
    """

    type = f"{RepositoryReleaseNotificationBuilder.type}.community-required"

    @classmethod
    def build(
        cls,
        provider: str,
        generic_repository: GenericRepository,
        generic_release: GenericRelease,
        draft,
    ):
        """Build the notification."""
        notification = super().build(provider, generic_repository, generic_release)
        notification.context["draft"] = EntityResolverRegistry.reference_entity(draft)
        return notification

    context = [EntityResolve(key="draft")]


class RepositoryReleaseCommunitySubmittedNotificationBuilder(
    RepositoryReleaseNotificationBuilder
):
    """Notification builder for when a release is submitted for review by a community."""

    type = f"{RepositoryReleaseNotificationBuilder.type}.community-submitted"

    @classmethod
    def build(
        cls,
        provider: str,
        generic_repository: GenericRepository,
        generic_release: GenericRelease,
        request,
        community,
        warnings: list[str],
    ):
        """Build the notification."""
        notification = super().build(provider, generic_repository, generic_release)
        notification.context["request"] = EntityResolverRegistry.reference_entity(
            request
        )
        notification.context["community"] = EntityResolverRegistry.reference_entity(
            community
        )
        notification.context["warnings"] = warnings
        return notification

    context = [EntityResolve(key="request"), EntityResolve(key="community")]
