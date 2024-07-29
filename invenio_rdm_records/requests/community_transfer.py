# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Community transfer request implementation."""

from invenio_i18n import lazy_gettext as _
from invenio_requests.customizations import RequestType, actions


class AcceptCommunityTransfer(actions.AcceptAction):
    """Represents an accept action used to accept a communtiy transfer request."""

    def execute(self, identity, uow):
        """Executes approve action."""
        # Step 1 - move communities to new target using communities service
        # Step 2 - move records to new parent using community records service
        super().execute(identity, uow)


class CommunityTransferRequest(RequestType):
    """Request to transfer a community to a new parent."""

    type_id = "community_transfer"
    name = _("Community transfer")

    creator_can_be_none = False
    topic_can_be_none = False
    allowed_creator_ref_types = ["user"]
    allowed_receiver_ref_types = ["group"]  # administrators
    allowed_topic_ref_types = ["community"]

    available_actions = {
        "delete": actions.DeleteAction,
        "submit": actions.SubmitAction,
        "create": actions.CreateAction,
        "cancel": actions.CancelAction,
        # Custom implemented actions
        "accept": AcceptCommunityTransfer,
        "decline": actions.DeclineAction,
    }
