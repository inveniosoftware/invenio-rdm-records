# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN
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
def c(running_app, db):
    """A basic community fixture"""
    _c = Community.create({})
    _c.commit()
    db.session.commit()
    return _c


def test_community_integration(db, c, running_app, minimal_record):
    """Basic smoke test for communities integration."""
    draft = RDMDraft.create(minimal_record)
    draft.commit()
    db.session.commit()
    record = RDMRecord.publish(draft)
    record.commit()
    db.session.commit()
    record.parent.communities.add(c, default=True)
    record.parent.commit()
    record.commit()
    assert record.dumps()["parent"]["communities"] == {
        "default": str(c.id),
        "ids": [str(c.id)],
    }
    db.session.commit()
