# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 CERN.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Content moderation for communities."""

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_records_resources.services.records.components import ServiceComponent
from invenio_records_resources.services.uow import TaskOp
from invenio_requests.tasks import request_moderation


class BaseHandler:
    """Base class for content moderation handlers."""

    def create(self, identity, record=None, data=None, uow=None, **kwargs):
        """Create handler."""
        pass

    def update(self, identity, record=None, data=None, uow=None, **kwargs):
        """Update handler."""
        pass

    def delete(self, identity, data=None, record=None, uow=None, **kwargs):
        """Delete handler."""
        pass


class UserModerationHandler(BaseHandler):
    """Creates user moderation request if the user publishing is not verified."""

    @property
    def enabled(self):
        """Check if user moderation is enabled."""
        return current_app.config["RDM_USER_MODERATION_ENABLED"]

    def run(self, identity, record=None, uow=None):
        """Calculate the moderation score for a given record or draft."""
        if self.enabled:
            # If the publisher is the system process, we don't want to create a moderation request.
            # Even if the record being published is owned by a user that is not system
            if identity == system_identity:
                return

            # resolve current user and check if they are verified
            is_verified = identity.user.verified_at is not None
            if not is_verified:
                # Spawn a task to request moderation.
                uow.register(TaskOp(request_moderation, user_id=identity.id))

    def create(self, identity, record=None, data=None, uow=None, **kwargs):
        """Handle create."""
        self.run(identity, record=record, uow=uow)

    def update(self, identity, record=None, data=None, uow=None, **kwargs):
        """Handle update."""
        self.run(identity, record=record, uow=uow)


class ContentModerationComponent(ServiceComponent):
    """Service component for content moderation."""

    def handler_for(action):
        """Get the handlers for an action."""

        def _handler_method(self, *args, **kwargs):
            handlers = current_app.config.get(
                "RDM_COMMUNITY_CONTENT_MODERATION_HANDLERS", []
            )
            for handler in handlers:
                action_method = getattr(handler, action, None)
                if action_method:
                    action_method(*args, **kwargs, uow=self.uow)

        return _handler_method

    create = handler_for("create")
    update = handler_for("update")
    delete = handler_for("delete")

    del handler_for
