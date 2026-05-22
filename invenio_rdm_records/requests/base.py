# SPDX-FileCopyrightText: 2021-2026 CERN.
# SPDX-FileCopyrightText: 2025 Northwestern University.
# SPDX-License-Identifier: MIT

"""Base class for review requests."""

from invenio_records_resources.services import EndpointLink
from invenio_requests.customizations import RequestType
from invenio_requests.services.events.config import request_event_anchor


class BaseRequest(RequestType):
    """Base class for all RDM requests rendered via UI."""

    links_item = {
        "self_html": EndpointLink(
            "invenio_app_rdm_requests.user_dashboard_request_view",
            params=["request_pid_value"],
            vars=lambda obj, vars: vars.update(request_pid_value=vars["request"].id),
            anchor=request_event_anchor,
        ),
    }


class ReviewRequest(BaseRequest):
    """Base class for all review requests."""

    block_publish = True
