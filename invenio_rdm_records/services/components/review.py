# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM service component for request integration."""


from flask_babelex import lazy_gettext as _
from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_requests import current_requests_service

from ..errors import ReviewExistsError, ReviewStateError


class ReviewComponent(ServiceComponent):
    """Service component for request integration."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Create the review if requested."""
        data = data.get("parent", {}).get("review")
        if data is not None:
            self.service.review.create(identity, data, record, uow=self.uow)

    def delete_draft(self, identity, draft=None, record=None, force=False):
        """Delete a draft."""
        review = draft.parent.review
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

        # Delete draft request's. A request in any other state is left as-is,
        # to allow users to see the request even if it was removed.
        if review.status == "created":
            current_requests_service.delete(
                identity, draft.parent.review.id, uow=self.uow
            )

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Block publishing if required.."""
        review = draft.parent.review
        if review is None:
            return
        if getattr(review.type, "block_publish", True) and not review.is_closed:
            raise ReviewExistsError()
