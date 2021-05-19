# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the relations component."""

import pytest

from invenio_rdm_records.proxies import current_rdm_records


@pytest.fixture()
def service(app):
    """The record service."""
    return current_rdm_records.records_service


def test_dereferencing(
        service, minimal_record, identity_simple, location, lang):
    """Read and read draft should dereference the record."""
    idty = identity_simple
    minimal_record['metadata']['languages'] = [{'id': 'eng'}]

    # Create
    draft = service.create(idty, minimal_record)
    assert 'title' in draft.data['metadata']['languages'][0]

    # Read draft
    draft = service.read_draft(draft.id, idty)
    assert 'title' in draft.data['metadata']['languages'][0]

    # Update draft
    draft = service.update_draft(draft.id, idty, draft.data)
    assert 'title' in draft.data['metadata']['languages'][0]

    # Publish
    record = service.publish(draft.id, idty)
    assert 'title' in record.data['metadata']['languages'][0]
