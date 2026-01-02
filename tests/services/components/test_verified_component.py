# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Tests for the service ContentModerationComponent."""

import pytest
from invenio_requests.proxies import current_requests_service

from invenio_rdm_records.proxies import current_rdm_records


@pytest.fixture()
def service(running_app):
    """The record service."""
    return current_rdm_records.records_service


def test_verified_content(service, minimal_record, verified_user, mod_identity):
    """Tests verified component when a user is already verified.

    For this test, no moderation requests are created since the user is already verified.
    """
    # Create
    draft = service.create(verified_user.identity, minimal_record)
    assert draft

    # Publish record
    record = service.publish(verified_user.identity, draft.id)
    assert record

    # No request was created
    search = current_requests_service.search(mod_identity)
    assert search.total == 0


def test_unverified_content(service, minimal_record, unverified_user, mod_identity):
    """Tests verified component when a user is not verified.

    For this test, a moderation request is created since the user is not verified.
    """
    # Create
    draft = service.create(unverified_user.identity, minimal_record)
    assert draft

    # Publish record
    record = service.publish(unverified_user.identity, draft.id)
    assert record

    # Request was created
    search = current_requests_service.search(mod_identity)
    assert search.total == 1
    hits = search.to_dict()["hits"]["hits"]
    hit = hits[0]
    assert hit["topic"]["user"] == str(unverified_user.id)
