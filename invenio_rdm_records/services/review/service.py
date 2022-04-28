# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Review Service."""

from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_drafts_resources.services.records import RecordService
from invenio_records_resources.services.uow import RecordCommitOp, \
    RecordIndexOp, unit_of_work
from invenio_requests import current_request_type_registry, \
    current_requests_service
from invenio_requests.resolvers.registry import ResolverRegistry
from marshmallow import ValidationError

from ..errors import ReviewExistsError, ReviewNotFoundError, ReviewStateError


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
        return current_app.config.get('RDM_RECORDS_REVIEWS', [])

    @unit_of_work()
    def create(self, identity, data, record, uow=None):
        """Create a new review request in draft state (to be completed."""
        if record.parent.review is not None:
            raise ReviewExistsError(
                _('A review already exists for this record'))
        # Validate that record has not been published.
        if record.is_published or record.versions.index > 1:
            raise ReviewStateError(
                _("You cannot create a review for an already published "
                  "record.")
            )

        # Validate the review type (only review requests are valid)
        type_ = current_request_type_registry.lookup(
            data.pop('type', None), quiet=True)
        if type_ is None or type_.type_id not in self.supported_types:
            raise ValidationError(
                _('Invalid review type.'),
                field_name='type'
            )

        # Resolve receiver
        receiver = ResolverRegistry.resolve_entity_proxy(
            data.pop('receiver', None)).resolve()

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
        # Delgate to requests service to create the request
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, 'read_draft', record=draft)

        if draft.parent.review is None:
            raise ReviewNotFoundError()

        return current_requests_service.read(identity, draft.parent.review.id)

    @unit_of_work()
    def update(self, identity, id_, data, revision_id=None, uow=None):
        """Create or update an existing review."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, 'update_draft', record=draft)

        # If an existing review exists, delete it.
        if draft.parent.review is not None:
            self.delete(identity, id_, uow=uow)
            draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        return self.create(identity, data, draft, uow=uow)

    @unit_of_work()
    def delete(self, identity, id_, revision_id=None, uow=None):
        """Delete a review."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, 'update_draft', record=draft)

        # Preconditions
        if draft.parent.review is None:
            raise ReviewNotFoundError()

        if draft.is_published:
            raise ReviewStateError(
                _("You cannot delete a review for a draft that has already "
                  "been published.")
            )

        if draft.parent.review.is_open:
            raise ReviewStateError(_("An open review cannot be deleted."))

        # Keep the request when not open or not closed so that the user can see
        # the request's events. The request is deleted only when in `draft`
        # status
        if not (draft.parent.review.is_closed or draft.parent.review.is_open):
            current_requests_service.delete(
                identity,
                draft.parent.review.id,
                uow=uow
            )
        # Unset on record
        draft.parent.review = None
        uow.register(RecordCommitOp(draft.parent))
        uow.register(RecordIndexOp(draft, indexer=self.indexer))
        return True

    @unit_of_work()
    def submit(self, identity, id_, data=None, revision_id=None, uow=None):
        """Submit record for review."""
        # Get record and check permission
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, 'update_draft', record=draft)

        # Preconditions
        if draft.parent.review is None:
            raise ReviewNotFoundError()

        # All other preconditions can be checked by the action itself which can
        # raise appropriate exceptions.
        request_item = current_requests_service.execute_action(
            identity, draft.parent.review.id, 'submit', data=data, uow=uow)

        # TODO: this shouldn't be required BUT because of the caching mechanism
        # in the review systemfield, the review should be set with the updated
        # request object
        draft.parent.review = request_item._request
        uow.register(RecordCommitOp(draft.parent))
        uow.register(RecordIndexOp(draft, indexer=self.indexer))

        return request_item
