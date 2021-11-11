# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Review Service."""

from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_access.permissions import system_process
from invenio_drafts_resources.services.records import RecordService
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work
from invenio_requests import current_registry, current_requests_service
from invenio_requests.resolvers import ResolverRegistry
from marshmallow import ValidationError


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
        # Validate the review type (only review requests are valid)
        type_ = current_registry.lookup(
            data.pop('request_type', None),
            quiet=True
        )
        if type_ is None or type_.type_id not in self.supported_types:
            raise ValidationError(_('Invalid review type.'))

        # Resolve receiver
        # TODO: problem - blr is not as persistent as the uuid (people can
        # change it)
        receiver = ResolverRegistry.resolve_entity_proxy(
            data.pop('receiver', None))

        # TODO: remove so it's not needed Defaults
        data['title'] = ''

        # Delgate to requests service to create the request
        request_item = current_requests_service.create(
            identity,
            data,
            type_,
            receiver.resolve(),
            topic=record,
            uow=uow,
        )

        # Set the request on the record and commit the record
        # TODO: make a system field - record.parent.review = ...
        record.parent['review'] = {'id': request_item.id}
        uow.register(RecordCommitOp(record.parent))

        return request_item

    def read(self, id_, identity):
        """."""
        pass

    @unit_of_work()
    def update(self, id_, identity, data, revision_id=None, uow=None):
        """."""
        pass

    @unit_of_work()
    def delete(self, id_, identity, revision_id=None, uow=None):
        """."""
        # Only allow deletion if never published
        # Allow deletion in draft, declined, expired, cancelled, state
        # Disallow deletion in open, accepted state
        # record.parent.review = None
        # record
        # requesttype.delete()
        pass

    @unit_of_work()
    def submit(self, id_, identity, data=None, revision_id=None, uow=None):
        """Submit record for review."""
        # Get record and check permission
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, 'update_draft', record=draft)

        # Get request id
        request_id = draft.parent['review']['id']

        # - validate_draft
        # Delegate to service to submit request which should do:
        # - change state and send request to receiver (i.e. send an event:
        #   state change)
        # - Send a redirect to /api/records/:id/draft/request?
        # - Validate comment data.
        # - Set request title to record title.
        request = current_requests_service.execute_action(
            identity, request_id, 'submit', data=data, uow=uow)
        return request
