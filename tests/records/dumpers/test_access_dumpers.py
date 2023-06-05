# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the access-control dumpers."""

import pytest
from invenio_records.dumpers import SearchDumper

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records import RDMDraft, RDMParent
from invenio_rdm_records.records.dumpers import GrantTokensDumperExt
from invenio_rdm_records.records.systemfields.access import Grant


def test_grant_tokens_dumper(app, db, minimal_record, location):
    """Test grant token dumper extension implementation."""
    dumper = SearchDumper(extensions=[GrantTokensDumperExt("access.grant_tokens")])

    data = {
        "access": {
            "grants": [
                {"subject": {"type": "user", "id": "1"}, "permission": "view"},
                {"subject": {"type": "user", "id": "2"}, "permission": "manage"},
            ]
        }
    }

    # Create the parent record
    parent = RDMParent.create(data)
    parent.commit()
    db.session.commit()

    grant1 = parent.access.grants[0]
    grant2 = parent.access.grants[1]

    # Dump it
    dump = parent.dumps(dumper=dumper)
    assert len(dump["access"]["grant_tokens"]) == 2
    assert grant1.to_token() in dump["access"]["grant_tokens"]
    assert grant2.to_token() in dump["access"]["grant_tokens"]

    # Load it
    new_record = RDMParent.loads(dump, loader=dumper)
    assert "grant_tokens" not in new_record["access"]
    assert "grant_tokens" not in new_record["access"]


# TODO re-enable after grants have been enabled in the schema
@pytest.mark.skip
def test_grant_tokens_dumper_query(
    app, db, minimal_record, users, identity_simple, location
):
    """Test grant token dumper extension queries."""
    id1 = str(users[0].id)
    id2 = str(users[1].id)
    grant1 = Grant.from_dict({"subject": "user", "id": id1, "level": "view"})
    grant2 = Grant.from_dict({"subject": "user", "id": id2, "level": "manage"})
    grant3 = Grant.from_dict({"subject": "user", "id": id1, "level": "viewfull"})

    minimal_record["access"]["grants"] = [
        grant1.to_dict(),
        grant2.to_dict(),
    ]

    # Create the record
    service = current_rdm_records.records_service
    service.create(identity_simple, minimal_record)

    minimal_record["access"]["grants"] = [
        grant2.to_dict(),
    ]

    service.create(identity_simple, minimal_record)

    RDMDraft.index.refresh()

    # Search for it
    assert (
        service.search(
            identity_simple,
            {"q": "access.grant_tokens:{}".format(grant1.to_token())},
            status="draft",
        ).total
        == 1
    )

    assert (
        service.search(
            identity_simple,
            {"q": "access.grant_tokens:{}".format(grant2.to_token())},
            status="draft",
        ).total
        == 2
    )

    assert (
        service.search(
            identity_simple,
            {"q": "access.grant_tokens:{}".format(grant3.to_token())},
            status="draft",
        ).total
        == 0
    )

    assert (
        service.search(
            identity_simple,
            {"q": "access.grant_tokens:actually.invalid.token"},
            status="draft",
        ).total
        == 0
    )
