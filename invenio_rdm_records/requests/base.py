# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base class for review requests."""

from invenio_requests.customizations import RequestType


class BaseRequest(RequestType):
    """Base class for all RDM requests."""

    def _update_link_config(self, **context_values):
        """Add the /me prefix for the self_html links."""
        prefix = "/me"
        return {"ui": context_values["ui"] + prefix}


class ReviewRequest(BaseRequest):
    """Base class for all review requests."""

    block_publish = True
