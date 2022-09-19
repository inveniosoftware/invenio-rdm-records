# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the relations component."""

import pytest

from invenio_rdm_records.proxies import current_rdm_records


@pytest.fixture()
def service(running_app):
    """The record service."""
    return current_rdm_records.records_service


def test_dereferencing(service, minimal_record, identity_simple):
    """Read and read draft should dereference the record."""
    idty = identity_simple
    minimal_record["metadata"]["languages"] = [{"id": "eng"}]

    # Create
    draft = service.create(idty, minimal_record)
    assert "title" in draft.data["metadata"]["languages"][0]

    # Read draft
    draft = service.read_draft(idty, draft.id)
    assert "title" in draft.data["metadata"]["languages"][0]

    # Update draft
    draft = service.update_draft(idty, draft.id, draft.data)
    assert "title" in draft.data["metadata"]["languages"][0]

    # Publish
    record = service.publish(idty, draft.id)
    assert "title" in record.data["metadata"]["languages"][0]
