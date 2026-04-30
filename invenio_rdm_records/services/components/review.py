# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM service component for request integration."""

from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_i18n import lazy_gettext as _
from invenio_requests import current_requests_service

from invenio_rdm_records.services.review.policy import NewRecordVersionReviewPolicy

from ...proxies import current_rdm_records_service
from ...requests.community_submission import CommunitySubmission
from ..errors import ReviewExistsError, ReviewStateError


class ReviewComponent(ServiceComponent):
    """Service component for request integration."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Create the review if requested."""
        parent_review = data.get("parent", {}).get("review")
        if parent_review is not None:
            self.service.review.create(identity, parent_review, record, uow=self.uow)

    def delete_draft(self, identity, draft=None, record=None, force=False):
        """Delete a draft."""
        review = draft.get_own_or_parent_review()
        if review is None:
            return
        # TODO: once draft status has been changed to not be considered open
        # the condition "review.status !=" can be removed.
        if review.is_open:
            raise ReviewStateError(
                _(
                    "You cannot delete a draft with an open review. Please "
                    "cancel the review first."
                )
            )

        # Delete draft's request. A request in any other state is left as-is,
        # to allow users to see the request even if it was removed.
        if review.status == "created":
            current_requests_service.delete(identity, review.id, uow=self.uow)

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Block publishing if required.."""
        review = draft.get_own_or_parent_review()
        if review is None:
            return
        if getattr(review.type, "block_publish", True) and not review.is_closed:
            raise ReviewExistsError(
                _(
                    "You cannot publish a draft with an open review request. Please cancel the review request first."
                )
            )

    def new_version(self, identity, draft=None, record=None):
        """
        Create a review for a new record version if required for the identity.

        If the identity does not have the `skip_review_for_new_version` permission, each new version of existing published records
        they create must go through a review by the parent record's default community.
        """
        assert draft is not None and record is not None
        # If the parent record does not have a default community, we do not need to create a review.
        default_community = record.parent.communities.default
        if default_community is None:
            return

        policy: NewRecordVersionReviewPolicy = (
            self.service.config.new_version_review_policy
        )
        if policy.requires_review(identity, draft):
            self.service.review.create(
                identity,
                {
                    "type": CommunitySubmission.type_id,
                    "receiver": {"community": default_community.id},
                },
                draft,
                uow=self.uow,
                assign_request_to_record=True,
            )
