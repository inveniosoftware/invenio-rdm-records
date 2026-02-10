# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Notification builders for VCS.
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
    ):
        notification = super().build(provider, generic_repository, generic_release)
        notification.context["record"] = EntityResolverRegistry.reference_entity(record)
        return notification

    context = [EntityResolve(key="record")]


class RepositoryReleaseFailureNotificationBuilder(RepositoryReleaseNotificationBuilder):
    """Notification builder for failed repository release events."""

    type = f"{RepositoryReleaseNotificationBuilder.type}.failure"

    @classmethod
    def build(
        cls,
        provider: str,
        generic_repository: GenericRepository,
        generic_release: GenericRelease,
        draft,
        error_message: str,
    ):
        notification = super().build(provider, generic_repository, generic_release)
        notification.context["draft"] = EntityResolverRegistry.reference_entity(draft)
        notification.context["error_message"] = error_message
        return notification

    context = [EntityResolve(key="draft")]


class RepositoryReleaseCommunityRequiredNotificationBuilder(
    RepositoryReleaseNotificationBuilder
):
    type = f"{RepositoryReleaseNotificationBuilder.type}.community-required"

    @classmethod
    def build(
        cls,
        provider: str,
        generic_repository: GenericRepository,
        generic_release: GenericRelease,
        draft,
    ):
        notification = super().build(provider, generic_repository, generic_release)
        notification.context["draft"] = EntityResolverRegistry.reference_entity(draft)
        return notification

    context = [EntityResolve(key="draft")]
