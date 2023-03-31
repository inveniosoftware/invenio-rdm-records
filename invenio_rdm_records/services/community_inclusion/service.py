# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Community Inclusion Service."""

from flask import current_app
from invenio_communities import current_communities
from invenio_i18n import lazy_gettext as _
from invenio_requests import current_requests_service

from invenio_rdm_records.requests.community_inclusion import (
    CommunityInclusion,
    is_access_restriction_valid,
)
from invenio_rdm_records.requests.community_submission import CommunitySubmission
from invenio_rdm_records.services.errors import InvalidAccessRestrictions


class CommunityInclusionService:
    """Service for including a record in a community.

    The RDM Requests service wraps some operations of the generic requests service,
    implementing RDM business logic.

    Note: this service is meant to be used by other services, and not by a resource.
    The uow should be passed by the caller.
    """

    @property
    def supported_types(self):
        """Supported request types."""
        types = {CommunitySubmission.type_id, CommunityInclusion.type_id}
        types.update(current_app.config.get("RDM_RECORDS_REVIEWS", []))
        return types

    def submit(self, identity, record, community, request, data, uow):
        """Submit a request to include a record in a community.

        It ensures that public records cannot be included in restricted communities.
        """
        if request.type.type_id not in self.supported_types:
            raise ValueError("Invalid request type.")

        # validate record and community access
        if not is_access_restriction_valid(record, community):
            raise InvalidAccessRestrictions()

        # All other preconditions can be checked by the action itself which can
        # raise appropriate exceptions.
        return current_requests_service.execute_action(
            identity, request.id, "submit", data=data, uow=uow
        )

    def include(self, identity, community, request, uow):
        """Accept the request to include the record in the community.

        Request will be accepted based on community policy and identity permissions
        """
        if request.type.type_id not in self.supported_types:
            raise ValueError("Invalid request type.")

        can_include_directly = current_communities.service.check_permission(
            identity, "include_directly", record=community
        )

        if can_include_directly:
            request_item = current_requests_service.execute_action(
                identity, request.id, "accept", data=None, uow=uow
            )
        else:
            request_item = current_requests_service.read(identity, request.id)

        return request_item
