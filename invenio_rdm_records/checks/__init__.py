# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Invenio-Checks integration.

To enable the integration, add the following to your configuration:

.. code-block:: python

    # Hook into community request actions
    from invenio_rdm_records.checks import requests as checks_requests
    RDM_COMMUNITY_SUBMISSION_REQUEST_CLS = checks_requests.CommunitySubmission
    RDM_COMMUNITY_INCLUSION_REQUEST_CLS = checks_requests.CommunityInclusion

    # Enable the feature flag
    CHECKS_ENABLED = True
"""
