# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Review Service."""

from flask import current_app
from invenio_communities import current_communities
from invenio_drafts_resources.services.records import RecordService
from invenio_drafts_resources.services.records.uow import ParentRecordCommitOp
from invenio_i18n import lazy_gettext as _
from invenio_notifications.services.uow import NotificationOp
from invenio_records_resources.services.uow import RecordIndexOp, unit_of_work
from invenio_requests import current_request_type_registry, current_requests_service
from invenio_requests.resolvers.registry import ResolverRegistry
from marshmallow import ValidationError

from ...notifications.builders import CommunityInclusionSubmittedNotificationBuilder
from ...proxies import current_rdm_records
from ...requests.decorators import request_next_link
from ..errors import (
    RecordSubmissionClosedCommunityError,
    ReviewExistsError,
    ReviewNotFoundError,
    ReviewStateError,
)


class ReviewService(RecordService):
    """Record review service.

    The review service is in charge of creating a review request.

    The request service is in charge of checking if an identity has permission
    to a given receiver (e.g. a restricted community).

    The request service validates if a receiver/topic is allowed for a given
    request type.

    A request type action is in charge of checking further properties - e.g.
    the submit action can check if the member policy of a community is open or
    closed.
    """

    @property
    def supported_types(self):
        """Supported review types."""
        return current_app.config.get("RDM_RECORDS_REVIEWS", [])

    def _validate_request_type(self, request_type):
        """Validates the request type."""
        type_ = current_request_type_registry.lookup(request_type, quiet=True)
        if type_ is None or type_.type_id not in self.supported_types:
            raise ValidationError(_("Invalid review type."), field_name="type")
        return type_

    @unit_of_work()
    def create(self, identity, data, record, uow=None):
        """Create a new review request in draft state (to be completed."""
        if record.parent.review is not None:
            raise ReviewExistsError(_("A review already exists for this record"))
        # Validate that record has not been published.
        if record.is_published or record.versions.index > 1:
            raise ReviewStateError(
                _("You cannot create a review for an already published record.")
            )

        # Validate the review type (only review requests are valid)
        type_ = self._validate_request_type(data.pop("type", None))

        # Resolve receiver
        receiver = ResolverRegistry.resolve_entity_proxy(
            data.pop("receiver", None)
        ).resolve()

        # Delegate to requests service to create the request
        request_item = current_requests_service.create(
            identity,
            data,
            type_,
            receiver,
            topic=record,
            uow=uow,
        )

        # Set the request on the record and commit the record
        record.parent.review = request_item._request
        uow.register(ParentRecordCommitOp(record.parent))

        return request_item

    def read(self, identity, id_):
        """Read the review."""
        # Delegate to requests service to create the request
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "read_draft", record=draft)

        if draft.parent.review is None:
            raise ReviewNotFoundError()

        request_type = draft.parent.review.get_object()["type"]
        self._validate_request_type(request_type)

        return current_requests_service.read(identity, draft.parent.review.id)

    @unit_of_work()
    def update(self, identity, id_, data, revision_id=None, uow=None):
        """Create or update an existing review."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "update_draft", record=draft)

        # If an existing review exists, delete it.
        if draft.parent.review is not None:
            self.delete(identity, id_, uow=uow)
            draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        return self.create(identity, data, draft, uow=uow)

    @unit_of_work()
    def delete(self, identity, id_, revision_id=None, uow=None):
        """Delete a review."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "update_draft", record=draft)

        # Preconditions
        if draft.parent.review is None:
            raise ReviewNotFoundError()
        request_type = draft.parent.review.get_object()["type"]
        self._validate_request_type(request_type)

        if draft.is_published:
            raise ReviewStateError(
                _(
                    "You cannot delete a review for a draft that has already "
                    "been published."
                )
            )

        if draft.parent.review.is_open:
            raise ReviewStateError(_("An open review cannot be deleted."))

        # Keep the request when not open or not closed so that the user can see
        # the request's events. The request is deleted only when in `draft`
        # status
        if not (draft.parent.review.is_closed or draft.parent.review.is_open):
            current_requests_service.delete(identity, draft.parent.review.id, uow=uow)
        # Unset on record
        draft.parent.review = None
        uow.register(ParentRecordCommitOp(draft.parent))
        uow.register(RecordIndexOp(draft, indexer=self.indexer))
        return True

    @request_next_link()
    @unit_of_work()
    def submit(self, identity, id_, data=None, require_review=False, uow=None):
        """Submit record for review or direct publish to the community."""
        if not isinstance(require_review, bool):
            raise ValidationError(
                _("Must be a boolean, true or false"),
                field_name="require_review",
            )

        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        # Preconditions
        if draft.parent.review is None:
            raise ReviewNotFoundError()

        request_type = draft.parent.review.get_object()["type"]
        self._validate_request_type(request_type)

        # since it is submit review action, assume the receiver is community
        community = draft.parent.review.receiver.resolve()

        # Check permission
        self.require_permission(identity, "update_draft", record=draft)

        community_id = (
            draft.parent.review.get_object().get("receiver", {}).get("community", "")
        )
        can_submit_record = current_communities.service.config.permission_policy_cls(
            "submit_record",
            community_id=community_id,
            record=community,
        ).allows(identity)

        if not can_submit_record:
            raise RecordSubmissionClosedCommunityError()

        # create review request
        request_item = current_rdm_records.community_inclusion_service.submit(
            identity, draft, community, draft.parent.review, data, uow
        )
        request = request_item._request

        # This shouldn't be required BUT because of the caching mechanism
        # in the review systemfield, the review should be set with the updated
        # request object
        draft.parent.review = request
        uow.register(ParentRecordCommitOp(draft.parent))
        uow.register(RecordIndexOp(draft, indexer=self.indexer))

        if not require_review:
            request_item = current_rdm_records.community_inclusion_service.include(
                identity, community, request, uow
            )

        uow.register(
            NotificationOp(
                CommunityInclusionSubmittedNotificationBuilder.build(
                    request_item._request,
                )
            )
        )
        return request_item
