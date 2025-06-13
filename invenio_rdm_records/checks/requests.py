# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Checks integration with community record requests."""

from flask import current_app
from invenio_checks.api import ChecksAPI
from invenio_checks.models import CheckRun
from invenio_db.uow import ModelDeleteOp

from ..requests import community_inclusion, community_submission

#
# Community submission request (draft review)
#
BaseCommunitySubmissionCreateAction = (
    community_submission.CommunitySubmission.available_actions["create"]
)
BaseCommunitySubmissionCancelAction = (
    community_submission.CommunitySubmission.available_actions["cancel"]
)


class SubmissionCreateAction(BaseCommunitySubmissionCreateAction):
    """Run checks on community submission creation (i.e. in the draft form)."""

    def execute(self, identity, uow):
        """Execute the create action."""
        super().execute(identity, uow)

        if current_app.config.get("CHECKS_ENABLED", False):
            # Run checks for the community submission
            draft = self.request.topic.resolve()
            community_ids = set()
            community = self.request.receiver.resolve()
            community_ids.add(str(community.id))
            if community.parent:
                community_ids.add(str(community.parent.id))

            configs = ChecksAPI.get_configs(community_ids)
            for config in configs:
                ChecksAPI.run_check(config, draft, uow)


class SubmissionCancelAction(BaseCommunitySubmissionCancelAction):
    """Clean-up checks on community submission cancelation."""

    def execute(self, identity, uow):
        """Remove checks runs for the community."""
        if current_app.config.get("CHECKS_ENABLED", False):
            # Get checks runs for the community submission
            draft = self.request.topic.resolve()
            community_ids = set()
            community = self.request.receiver.resolve()
            community_ids.add(str(community.id))
            if community.parent:
                community_ids.add(str(community.parent.id))

            configs = ChecksAPI.get_configs(community_ids)
            runs = CheckRun.query.filter(
                CheckRun.record_id == draft.id,
                CheckRun.is_draft.is_(True),
                CheckRun.config_id.in_({config.id for config in configs}),
            ).all()

            # Delete them
            for run in runs:
                uow.register(ModelDeleteOp(run))

        super().execute(identity, uow)


class CommunitySubmission(community_submission.CommunitySubmission):
    """Request to add a subcommunity to a Zenodo community."""

    available_actions = {
        **community_submission.CommunitySubmission.available_actions,
        # Override the create and cancle actions to handle check runs
        "create": SubmissionCreateAction,
        "cancel": SubmissionCancelAction,
    }


#
# Community inclusion request (record inclusion)
#
BaseCommunityInclussionSubmitAction = (
    community_inclusion.CommunityInclusion.available_actions["submit"]
)
BaseCommunityInclusionCancelAction = (
    community_inclusion.CommunityInclusion.available_actions["cancel"]
)


class InclusionSubmitAction(community_inclusion.SubmitAction):
    """Submit action."""

    def execute(self, identity, uow):
        """Execute the submit action."""
        super().execute(identity, uow)

        if current_app.config.get("CHECKS_ENABLED", False):
            # Run checks for the community submission
            record = self.request.topic.resolve()
            community_ids = set()
            community = self.request.receiver.resolve()
            community_ids.add(str(community.id))
            if community.parent:
                community_ids.add(str(community.parent.id))

            # Take into account existing communities
            for community in record.parent.communities:
                community_ids.add(str(community.id))
                community_parent_id = community.get("parent", {}).get("id")
                if community_parent_id:
                    community_ids.add(community_parent_id)

            configs = ChecksAPI.get_configs(community_ids)
            for config in configs:
                ChecksAPI.run_check(config, record, uow, is_draft=record.has_draft)


class InclusionCancelAction(BaseCommunityInclusionCancelAction):
    """Clean-up checks on community inclusion cancelation."""

    def execute(self, identity, uow):
        """Remove checks runs for the community."""
        if current_app.config.get("CHECKS_ENABLED", False):
            # Get checks runs for the community submission
            draft = self.request.topic.resolve()
            community_ids = set()
            community = self.request.receiver.resolve()
            community_ids.add(str(community.id))
            if community.parent:
                community_ids.add(str(community.parent.id))

            configs = ChecksAPI.get_configs(community_ids)
            runs = CheckRun.query.filter(
                CheckRun.record_id == draft.id,
                # NOTE: We don't filter by draft/record here, since we want to remove
                # all runs related to the community checks.
                CheckRun.config_id.in_({config.id for config in configs}),
            ).all()

            # Delete them
            for run in runs:
                uow.register(ModelDeleteOp(run))

        super().execute(identity, uow)


class CommunityInclusion(community_inclusion.CommunityInclusion):
    """Request for a published record to be included in a community."""

    available_actions = {
        **community_inclusion.CommunityInclusion.available_actions,
        # Override the submit and cancel action to handle checks
        "submit": InclusionSubmitAction,
        "cancel": InclusionCancelAction,
    }
