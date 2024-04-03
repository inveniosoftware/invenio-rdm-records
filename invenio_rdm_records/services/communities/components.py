# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record communities service components."""

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_communities.communities.records.systemfields.access import VisibilityEnum
from invenio_communities.communities.services.components import ChildrenComponent
from invenio_communities.communities.services.components import (
    CommunityAccessComponent as BaseAccessComponent,
)
from invenio_communities.communities.services.components import (
    CommunityDeletionComponent,
    CommunityParentComponent,
    CommunityThemeComponent,
    CustomFieldsComponent,
    FeaturedCommunityComponent,
    OAISetComponent,
    OwnershipComponent,
    PIDComponent,
)
from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.records.components import (
    MetadataComponent,
    RelationsComponent,
)
from invenio_requests.tasks import request_moderation
from invenio_search.engine import dsl

from ...proxies import current_community_records_service
from ..errors import InvalidCommunityVisibility


class CommunityAccessComponent(BaseAccessComponent):
    """Community access component."""

    def _check_visibility(self, identity, record):
        """Checks if the visibility change is allowed."""
        if VisibilityEnum(record.access.visibility) == VisibilityEnum.RESTRICTED:
            count_public_records = current_community_records_service.search(
                identity,
                community_id=record.id,
                extra_filter=dsl.Q("term", **{"access.record": "public"}),
            ).total
            if count_public_records > 0:
                raise InvalidCommunityVisibility(
                    reason=_("Cannot restrict a community with public records.")
                )

    def update(self, identity, data=None, record=None, **kwargs):
        """Update handler."""
        old_visibility = record.get("access", {}).get("visibility")
        new_visibility = data.get("access", {}).get("visibility")
        check_visibility = old_visibility != new_visibility

        super().update(identity, data, record, **kwargs)

        if check_visibility:
            self._check_visibility(identity, record)


class ContentModerationComponent(ServiceComponent):
    """Service component for content moderation."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Create a moderation request if the user is not verified."""
        if current_app.config["RDM_USER_MODERATION_ENABLED"]:
            # If the publisher is the system process, we don't want to create a moderation request.
            # Even if the record being published is owned by a user that is not system
            if identity == system_identity:
                return

            # resolve current user and check if they are verified
            is_verified = identity.user.verified_at is not None

            if not is_verified:
                # Spawn a task to request moderation.
                request_moderation.delay(identity.id)


CommunityServiceComponents = [
    MetadataComponent,
    CommunityThemeComponent,
    CustomFieldsComponent,
    PIDComponent,
    RelationsComponent,
    CommunityAccessComponent,
    OwnershipComponent,
    FeaturedCommunityComponent,
    OAISetComponent,
    ContentModerationComponent,
    CommunityDeletionComponent,
    ChildrenComponent,
    CommunityParentComponent,
]
