# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2025 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base class for review requests."""

from invenio_records_resources.services import EndpointLink
from invenio_requests.customizations import RequestType


class BaseRequest(RequestType):
    """Base class for all RDM requests."""

    links_item = {
        "self_html": EndpointLink(
            "invenio_app_rdm_requests.user_dashboard_request_view",
            params=["request_pid_value"],
            vars=lambda obj, vars: vars.update(request_pid_value=vars["request"].id),
        ),
    }


class ReviewRequest(BaseRequest):
    """Base class for all review requests."""

    block_publish = True
