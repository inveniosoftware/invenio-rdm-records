# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Community addition request."""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.uow import RecordCommitOp, RecordIndexOp
from invenio_requests.customizations import RequestType, actions
from invenio_requests.errors import CannotExecuteActionError

from invenio_rdm_records.services.errors import InvalidAccessRestrictions

from ..proxies import current_rdm_records_service as service


def is_access_restriction_valid(record, community):
    """Validate that public record cannot be added to restricted community."""
    is_record_public = record.access.protection.record == "public"
    is_community_restricted = community.access.visibility_is_restricted
    invalid = is_record_public and is_community_restricted
    return not invalid


#
# Actions
#
class SubmitAction(actions.SubmitAction):
    """Submit action."""

    def execute(self, identity, uow):
        """Execute the submit action."""
        record = self.request.topic.resolve()
        # Set the record's title as the request title.
        self.request["title"] = record.metadata["title"]
        super().execute(identity, uow)


class AcceptAction(actions.AcceptAction):
    """Accept action."""

    def execute(self, identity, uow):
        """Include record into community."""
        # Resolve the topic and community - the request type only allow for
        # community receivers and record topics.
        record = self.request.topic.resolve()
        community = self.request.receiver.resolve()

        # integrity check, it should never happen on a published record
        assert not record.parent.review

        if not is_access_restriction_valid(record, community):
            description = InvalidAccessRestrictions.description
            raise CannotExecuteActionError(description)

        # set the community to `default` if it is the first
        default = not record.parent.communities
        record.parent.communities.add(community, request=self.request, default=default)
        uow.register(RecordCommitOp(record.parent))
        uow.register(RecordIndexOp(record, indexer=service.indexer))

        super().execute(identity, uow)


#
# Request
#
class CommunityInclusion(RequestType):
    """Community inclusion request for adding a record to a community."""

    type_id = "community-inclusion"
    name = _("Community inclusion")

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
        "cancel": actions.CancelAction,
        "decline": actions.DeclineAction,
        "expire": actions.ExpireAction,
    }
