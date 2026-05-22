# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Subcommunity request types for RDM."""

from invenio_communities.subcommunities.services.request import (
    SubCommunityInvitationRequest,
    SubCommunityRequest,
)
from invenio_records_resources.services import EndpointLink
from invenio_requests.services.events.config import request_event_anchor


class RDMSubCommunityRequest(SubCommunityRequest):
    """Subcommunity request with RDM specific community dashboard links."""

    links_item = {
        "self_html": EndpointLink(
            "invenio_app_rdm_requests.community_dashboard_request_view",
            params=["pid_value", "request_pid_value"],
            vars=lambda obj, vars: vars.update(
                request_pid_value=vars["request"].id,
                pid_value=vars["request"].receiver.resolve().slug,
            ),
            anchor=request_event_anchor,
        ),
    }


class RDMSubCommunityInvitationRequest(SubCommunityInvitationRequest):
    """Subcommunity invitation request with RDM specific community dashboard links."""

    links_item = {
        "self_html": EndpointLink(
            "invenio_app_rdm_requests.community_dashboard_request_view",
            params=["pid_value", "request_pid_value"],
            vars=lambda obj, vars: vars.update(
                request_pid_value=vars["request"].id,
                pid_value=vars["request"].receiver.resolve().slug,
            ),
            anchor=request_event_anchor,
        ),
    }
