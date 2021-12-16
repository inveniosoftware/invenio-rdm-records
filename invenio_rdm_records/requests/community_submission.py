# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Community submission request."""

from flask_babelex import lazy_gettext as _
from invenio_records_resources.services.uow import RecordCommitOp
from invenio_requests.customizations import RequestAction

from ..proxies import current_rdm_records_service as service
from .base import ReviewRequest


#
# Actions
#
class SubmitAction(RequestAction):
    """Submit action."""

    status_from = ['draft']
    status_to = 'open'

    def can_execute(self, identity):
        """Validate if action can be executed."""
        draft = self.request.topic.resolve()
        service._validate_draft(identity, draft)
        return super().can_execute(identity)

    def execute(self, identity, uow):
        """Execute the submit action."""
        # Set the record's title as the request title.
        draft = self.request.topic.resolve()
        self.request['title'] = draft.metadata['title']
        super().execute(identity, uow)


class AcceptAction(RequestAction):
    """Accept action."""

    status_from = ['open']
    status_to = 'accepted'

    def can_execute(self, identity):
        """Check of the accpet action can be executed."""
        draft = self.request.topic.resolve()
        service._validate_draft(identity, draft)
        return True

    def execute(self, identity, uow):
        """Accept record into community."""
        # Resolve the topic and community - the request type only allow for
        # community receivers and record topics.
        draft = self.request.topic.resolve()
        community = self.request.receiver.resolve()

        # Unset review from record (still accessible from request)
        # The curator (receiver) should still have access, via the community
        # The creator (uploader) should also still have access, because
        # they're the uploader
        draft.parent.review = None

        # TODO:
        # - Put below into a service method
        # - Check permissions

        # Add community to record.
        is_default = self.request.type.set_as_default
        draft.parent.communities.add(
            community, request=self.request, default=is_default
        )
        uow.register(RecordCommitOp(draft.parent))

        # Publish the record
        # TODO: Ensure that the accpeting user has permissions to publish.
        service.publish(identity, draft.pid.pid_value, uow=uow)
        super().execute(identity, uow)


class DeclineAction(RequestAction):
    """Decline action."""

    status_from = ['open']
    status_to = 'declined'

    def execute(self, identity, uow):
        """Execute action."""
        # Unset review from record (still accessible from request)
        # This means that the receiver (curator) won't have access anymore
        # The creator (uploader) should still have access to the record/draft
        draft = self.request.topic.resolve()
        draft.parent.review = None
        super().execute(identity, uow)


class CancelAction(RequestAction):
    """Decline action."""

    status_from = ['open']
    status_to = 'cancelled'

    def execute(self, identity, uow):
        """Execute action."""
        # Remove draft from request
        # Same reasoning as in 'decline'
        draft = self.request.topic.resolve()
        draft.parent.review = None
        uow.register(RecordCommitOp(draft.parent))
        super().execute(identity, uow)


class ExpireAction(RequestAction):
    """Expire action."""

    status_from = ['open']
    status_to = 'expired'

    def execute(self, identity, uow):
        """Execute action."""
        # Remove draft from request
        # Same reasoning as in 'decline'
        draft = self.request.topic.resolve()
        draft.parent.review = None

        # TODO: What more to do? simply close the request? Similarly to
        # decline, how does a user resubmits the request to the same community.
        super().execute(identity, uow)


#
# Request
#
class CommunitySubmission(ReviewRequest):
    """Review request for submitting a record to a community."""

    type_id = 'community-submission'
    name = _('Community submission')

    block_publish = True
    set_as_default = True

    creator_can_be_none = False
    topic_can_be_none = False
    allowed_creator_ref_types = ['user']
    allowed_receiver_ref_types = ['community']
    allowed_topic_ref_types = ['record']

    available_actions = {
        "submit": SubmitAction,
        "accept": AcceptAction,
        "cancel": CancelAction,
        "decline": DeclineAction,
        "expire": ExpireAction,
    }
