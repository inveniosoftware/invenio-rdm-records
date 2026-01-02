# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""RDM service component for content moderation."""

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_records_resources.services.uow import TaskOp
from invenio_requests.tasks import request_moderation


class BaseHandler:
    """Base class for content moderation handlers."""

    def update_draft(
        self, identity, data=None, record=None, errors=None, uow=None, **kwargs
    ):
        """Update draft handler."""
        pass

    def delete_draft(
        self, identity, draft=None, record=None, force=False, uow=None, **kwargs
    ):
        """Delete draft handler."""
        pass

    def edit(self, identity, draft=None, record=None, uow=None, **kwargs):
        """Edit a record handler."""
        pass

    def new_version(self, identity, draft=None, record=None, uow=None, **kwargs):
        """New version handler."""
        pass

    def publish(self, identity, draft=None, record=None, uow=None, **kwargs):
        """Publish handler."""
        pass

    def post_publish(
        self, identity, record=None, is_published=False, uow=None, **kwargs
    ):
        """Post publish handler."""
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

            is_verified = record.parent.is_verified
            if not is_verified:
                # Spawn a task to request moderation.
                user_id = record.parent.access.owner.owner_id
                uow.register(TaskOp(request_moderation, user_id=user_id))

    def publish(self, identity, draft=None, record=None, uow=None, **kwargs):
        """Handle publish."""
        self.run(identity, record=record, uow=uow)


class ContentModerationComponent(ServiceComponent):
    """Service component for content moderation."""

    def handler_for(action):
        """Get the handlers for an action."""

        def _handler_method(self, *args, **kwargs):
            handlers = current_app.config.get("RDM_CONTENT_MODERATION_HANDLERS", [])
            for handler in handlers:
                action_method = getattr(handler, action, None)
                if action_method:
                    action_method(*args, **kwargs, uow=self.uow)

        return _handler_method

    update_draft = handler_for("update_draft")
    delete_draft = handler_for("delete_draft")
    edit = handler_for("edit")
    publish = handler_for("publish")
    post_publish = handler_for("post_publish")
    new_version = handler_for("new_version")

    del handler_for
