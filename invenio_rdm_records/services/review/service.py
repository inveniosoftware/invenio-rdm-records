# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Review Service."""

from flask import current_app
from invenio_communities import current_communities
from invenio_communities.communities.records.systemfields.access import CommunityAccess
from invenio_drafts_resources.services.records import RecordService
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    RecordIndexOp,
    unit_of_work,
)
from invenio_requests import current_request_type_registry, current_requests_service
from invenio_requests.resolvers.registry import ResolverRegistry
from invenio_requests.services.requests.links import RequestLink, RequestLinksTemplate
from marshmallow import ValidationError

from ...records.systemfields.access.field.record import AccessStatusEnum
from ..errors import (
    ReviewExistsError,
    ReviewInconsistentAccessRestrictions,
    ReviewNotFoundError,
    ReviewStateError,
)
from .links import RequestRecordLink


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

    def validate_request_type(self, request_type):
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
        type_ = self.validate_request_type(data.pop("type", None))

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
        uow.register(RecordCommitOp(record.parent))
        return request_item

    def read(self, identity, id_):
        """Read the review."""
        # Delegate to requests service to create the request
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "read_draft", record=draft)

        if draft.parent.review is None:
            raise ReviewNotFoundError()

        request_type = draft.parent.review.get_object()["type"]
        self.validate_request_type(request_type)

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
        self.validate_request_type(request_type)

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
        uow.register(RecordCommitOp(draft.parent))
        uow.register(RecordIndexOp(draft, indexer=self.indexer))
        return True

    @unit_of_work()
    def submit(
        self, identity, id_, data=None, require_review=False, revision_id=None, uow=None
    ):
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
        self.validate_request_type(request_type)

        # since it is submit review action, assume the receiver is community
        resolved_community = draft.parent.review.receiver.resolve()

        # create review request
        request_item = self._submit(
            identity, draft, resolved_community, data, revision_id, uow
        )

        try:
            # check if can direct publish
            current_communities.service.require_permission(
                identity, "direct_publish", record=resolved_community
            )
        except PermissionDeniedError:
            # review request is required
            require_review = True

        if not require_review:
            # Direct publish: auto-accept request, without any payload
            request_item = current_requests_service.execute_action(
                identity, request_item.data["id"], "accept", data=None, uow=uow
            )

        links_item = dict(
            current_requests_service.config.links_item,
            next_html=RequestRecordLink("{+ui}/records/{record_id}"),
        )
        if require_review:
            links_item.update(next_html=RequestLink("{+ui}/me/requests/{id}"))

        links_item_tpl = RequestLinksTemplate(
            links_item,
            current_requests_service.config.action_link,
            context={
                "permission_policy_cls": current_requests_service.config.permission_policy_cls,
            },
        )

        request_item.links_tpl = links_item_tpl
        return request_item

    def _submit(
        self, identity, draft, resolved_community, data=None, revision_id=None, uow=None
    ):
        """Submit record for review."""
        # Get record and check permission
        self.require_permission(identity, "update_draft", record=draft)

        assert "restricted" in CommunityAccess.VISIBILITY_LEVELS
        community_is_restricted = (
            resolved_community["access"]["visibility"] == "restricted"
        )

        record_is_restricted = draft.access.status == AccessStatusEnum.RESTRICTED

        if community_is_restricted and not record_is_restricted:
            raise ReviewInconsistentAccessRestrictions()

        # All other preconditions can be checked by the action itself which can
        # raise appropriate exceptions.
        request_item = current_requests_service.execute_action(
            identity, draft.parent.review.id, "submit", data=data, uow=uow
        )

        # TODO: this shouldn't be required BUT because of the caching mechanism
        # in the review systemfield, the review should be set with the updated
        # request object
        draft.parent.review = request_item._request
        uow.register(RecordCommitOp(draft.parent))
        uow.register(RecordIndexOp(draft, indexer=self.indexer))

        return request_item
