# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base class for review requests."""

from invenio_requests.customizations import BaseRequestType


class ReviewRequest(BaseRequestType):
    """Base class for all review requests."""

    block_publish = True
