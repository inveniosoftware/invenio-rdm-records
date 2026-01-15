# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2025 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base class for review requests."""

from invenio_requests.customizations import RequestType


class BaseRequest(RequestType):
    """Base class for all RDM requests."""

    endpoints_item = {
        "self_html": "invenio_app_rdm_requests.user_dashboard_request_view"
    }


class ReviewRequest(BaseRequest):
    """Base class for all review requests."""

    block_publish = True
