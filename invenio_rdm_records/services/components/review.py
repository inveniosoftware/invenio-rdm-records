# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM service component for request integration."""


from invenio_drafts_resources.services.records.components import \
    ServiceComponent


class ReviewComponent(ServiceComponent):
    """Service component for request integration."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Create the review if requested."""
        data = data.get("parent", {}).get("review")
        if data is not None:
            self.service.review.create(identity, data, record, uow=self.uow)

    def delete_draft(self, identity, draft=None, record=None, force=False):
        """Delete a draft."""
        # TODO: prevent deletion (similar to prevent publish if open requests
        # exists)
        # you can delete draft if in request in state: draft, cancelled,
        # declined, expired.
        # When you delete something that was cancelled, can the receiver still
        # see the request?
        pass

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        # TODO:
        # Block publishing if:
        # - a request exists AND
        # - the request type blocks publishing AND
        # - the request is in state draft, open.
        # What if request was declined, expired, cancelled and it's published?
        # Do we keep the association with the declined review.
        pass

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        # Do nothing

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        # Do nothing
