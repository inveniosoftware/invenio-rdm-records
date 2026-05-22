# SPDX-FileCopyrightText: 2025 CERN.
# SPDX-License-Identifier: MIT

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
