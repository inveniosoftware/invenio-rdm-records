# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Basic community integration test.

Note, most data layer tests are in Invenio-Communities where the system field
is defined.
"""

import pytest
from invenio_communities.communities.records.api import Community

from invenio_rdm_records.records.api import RDMDraft, RDMRecord


@pytest.fixture()
def community(running_app, db):
    """A basic community fixture"""
    comm = Community.create({})
    comm.slug = "test-community"
    comm.metadata = {"title": "Test Community"}
    comm.theme = {"brand": "test-theme-brand"}
    comm.commit()
    db.session.commit()
    return comm


def test_community_integration(db, community, running_app, minimal_record):
    """Basic smoke test for communities integration."""
    draft = RDMDraft.create(minimal_record)
    draft.commit()
    db.session.commit()
    record = RDMRecord.publish(draft)
    record.commit()
    db.session.commit()
    record.parent.communities.add(community, default=True)
    record.parent.commit()
    record.commit()
    db.session.commit()

    assert record.parent.communities.entries[0] == community
    dump = record.dumps()
    assert dump["parent"]["communities"]["default"] == str(community.id)
    assert dump["parent"]["communities"]["ids"] == [str(community.id)]
    entries = dump["parent"]["communities"]["entries"]
    assert len(entries) == 1
    assert entries[0]["id"] == str(community.id)
    assert entries[0]["slug"] == "test-community"
    assert entries[0]["metadata"]["title"] == "Test Community"
    assert entries[0]["theme"]["brand"] == "test-theme-brand"
    keys = entries[0].keys()
    assert {"id", "slug", "metadata", "theme", "created", "updated"} <= keys
