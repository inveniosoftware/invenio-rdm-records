# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests record's communities resources."""

import pytest

# from invenio_rdm_records.proxies import current_rdm_records


# @pytest.fixture()
# def service():
#     """Get the current RDM records service."""
#     return current_rdm_records.records_service


# @pytest.fixture()
# def published(uploader, minimal_record, community, service, running_app, db):
#     minimal_record["parent"] = {
#         "review": {
#             "type": "community-submission",
#             "receiver": {"community": community.data["id"]},
#         }
#     }

#     # Create draft with review
#     draft = service.create(uploader.identity, minimal_record)
#     # Publish
#     return service.publish(uploader.identity, draft.id)


# def test_add_community(uploader, published):
def test_add_community(client, uploader):
    """Fix me."""
    client = uploader.login(client)
    # resp = client.post(f"/records/{published.pid}/communities")
    resp = client.post(f"/records/random-id/communities")
    assert resp.status_code == 200
