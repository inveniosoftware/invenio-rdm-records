# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Community submission request."""

from invenio_drafts_resources.services.records.uow import ParentRecordCommitOp
from invenio_i18n import lazy_gettext as _
from invenio_notifications.services.uow import NotificationOp
from invenio_requests.customizations import actions

from ..notifications.builders import (
    CommunityInclusionAcceptNotificationBuilder,
    CommunityInclusionCancelNotificationBuilder,
    CommunityInclusionDeclineNotificationBuilder,
    CommunityInclusionExpireNotificationBuilder,
)
from ..proxies import current_rdm_records_service as service
from ..services.errors import InvalidAccessRestrictions
from .base import ReviewRequest
from .community_inclusion import is_access_restriction_valid


#
# Actions
#
class SubmitAction(actions.SubmitAction):
    """Submit action."""

    def execute(self, identity, uow):
        """Execute the submit action."""
        draft = self.request.topic.resolve()
        service._validate_draft(identity, draft)
        # Set the record's title as the request title.
        self.request["title"] = draft.metadata["title"]
        super().execute(identity, uow)


class AcceptAction(actions.AcceptAction):
    """Accept action."""

    def execute(self, identity, uow):
        """Accept record into community."""
        # Resolve the topic and community - the request type only allow for
        # community receivers and record topics.
        draft = self.request.topic.resolve()
        community = self.request.receiver.resolve()
        service._validate_draft(identity, draft)

        # validate record and community access
        if not is_access_restriction_valid(draft, community):
            raise InvalidAccessRestrictions()

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

        if getattr(community, "parent", None):
            draft.parent.communities.add(community.parent, request=self.request)

        uow.register(
            ParentRecordCommitOp(draft.parent, indexer_context=dict(service=service))
        )

        # Publish the record
        # TODO: Ensure that the accepting user has permissions to publish.
        service.publish(identity, draft.pid.pid_value, uow=uow)
        uow.register(
            NotificationOp(
                CommunityInclusionAcceptNotificationBuilder.build(
                    identity=identity, request=self.request
                )
            )
        )
        super().execute(identity, uow)


class DeclineAction(actions.DeclineAction):
    """Decline action."""

    def execute(self, identity, uow):
        """Execute action."""
        # Keeps the record and the review connected so the user can see the
        # outcome of the request
        # The receiver (curator) won't have access anymore to the draft
        # The creator (uploader) should still have access to the record/draft
        draft = self.request.topic.resolve()
        super().execute(identity, uow)

        # TODO: this shouldn't be required BUT because of the caching mechanism
        # in the review systemfield, the review should be set with the updated
        # request object
        draft.parent.review = self.request
        uow.register(
            ParentRecordCommitOp(draft.parent, indexer_context=dict(service=service))
        )
        uow.register(
            NotificationOp(
                CommunityInclusionDeclineNotificationBuilder.build(
                    identity=identity, request=self.request
                )
            )
        )


class CancelAction(actions.CancelAction):
    """Decline action."""

    def execute(self, identity, uow):
        """Execute action."""
        # Remove draft from request
        # Same reasoning as in 'decline'
        draft = self.request.topic.resolve()
        draft.parent.review = None
        uow.register(
            ParentRecordCommitOp(draft.parent, indexer_context=dict(service=service))
        )
        super().execute(identity, uow)
        uow.register(
            NotificationOp(
                CommunityInclusionCancelNotificationBuilder.build(
                    identity=identity, request=self.request
                )
            )
        )


class ExpireAction(actions.ExpireAction):
    """Expire action."""

    def execute(self, identity, uow):
        """Execute action."""
        # Same reasoning as in 'decline'
        draft = self.request.topic.resolve()

        # TODO: What more to do? simply close the request? Similarly to
        # decline, how does a user resubmits the request to the same community.
        super().execute(identity, uow)

        # TODO: this shouldn't be required BUT because of the caching mechanism
        # in the review systemfield, the review should be set with the updated
        # request object
        draft.parent.review = self.request
        uow.register(
            ParentRecordCommitOp(draft.parent, indexer_context=dict(service=service))
        )
        uow.register(
            NotificationOp(
                CommunityInclusionExpireNotificationBuilder.build(
                    identity=identity, request=self.request
                )
            )
        )


#
# Request
#
class CommunitySubmission(ReviewRequest):
    """Review request for submitting a record to a community."""

    type_id = "community-submission"
    name = _("Community submission")

    block_publish = True
    set_as_default = True

    creator_can_be_none = False
    topic_can_be_none = False
    allowed_creator_ref_types = ["user"]
    allowed_receiver_ref_types = ["community"]
    allowed_topic_ref_types = ["record"]
    needs_context = {
        "community_roles": ["owner", "manager", "curator"],
    }

    available_actions = {
        "create": actions.CreateAction,
        "submit": SubmitAction,
        "delete": actions.DeleteAction,
        "accept": AcceptAction,
        "decline": DeclineAction,
        "cancel": CancelAction,
        "expire": ExpireAction,
    }
