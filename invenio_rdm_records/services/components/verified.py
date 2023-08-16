# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""RDM service component for content moderation."""


from invenio_access.permissions import system_identity
from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_i18n import lazy_gettext as _

from invenio_rdm_records.services.tasks import request_moderation_async


class ContentModerationComponent(ServiceComponent):
    """Service component for content moderation."""

    def publish(self, identity, draft=None, record=None):
        """Create a moderation request if the user is not verified."""
        # If the publisher is the system process, we don't want to create a moderation request.
        # Even if the record being published is owned by a user that is not system
        if identity == system_identity:
            return

        is_verified = record.parent.is_verified

        if not is_verified:
            # Spawn a task to request moderation.
            request_moderation_async.delay(record.parent.access.owner.owner_id)
