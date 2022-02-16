# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2022 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Community submission request."""

from invenio_communities.permissions import CommunityRoleManager
from invenio_records_permissions.generators import Generator, SystemProcess
from invenio_requests.customizations.base import BaseRequestPermissionPolicy
from invenio_requests.customizations.base.permissions import Commenter, Creator


class SubmissionCommunityRole(Generator):
    """Allows community role based on submission."""

    def __init__(self, role):
        """Constructor."""
        self.role = role

    def needs(self, request=None, **kwargs):
        """Enabling Needs."""
        submission = request

        # if no submission, generator does nothing
        if submission is None:
            return []

        receiver = submission.receiver.reference_dict
        community_uuid = receiver.get("community")
        if community_uuid:
            return [
                CommunityRoleManager(community_uuid, self.role).to_need()
            ]

        return []


#
# Request
#
class CommunitySubmissionPermissionPolicy(BaseRequestPermissionPolicy):
    """Community Submission Permission Policy."""

    # Passed record is a submission
    curators = [
        SubmissionCommunityRole("owner"), SubmissionCommunityRole("manager"),
        SubmissionCommunityRole("curator"), SystemProcess()
    ]
    can_action_accept = curators
    can_action_decline = curators
    can_create_comment = curators + [Creator()]

    # Passed record is a comment
    can_update_comment = [Commenter(), SystemProcess()]
    # TODO: delete comment
    # can_delete_comment = [Commenter(), Receiver(), SystemProcess()]
