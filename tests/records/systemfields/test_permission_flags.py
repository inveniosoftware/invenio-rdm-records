# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test permission flags system field."""

import pytest
from invenio_access.permissions import system_identity

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records import RDMParent, RDMRecord


@pytest.fixture()
def service(running_app):
    """The record service."""
    return current_rdm_records.records_service


def test_permission_flags_valid(running_app, minimal_record):
    """Tests permission_flags get and set."""
    parent_data = {"permission_flags": {"can_community_read_files": True}}
    parent = RDMParent.create(parent_data)
    record = RDMRecord.create(minimal_record, parent=parent)

    # test get
    permission_flags = record.parent.permission_flags
    assert permission_flags == {"can_community_read_files": True}

    # test set
    new_data = {"new_permission_flag": False}
    parent.permission_flags = new_data
    assert parent.permission_flags == new_data

    # test absence of a flag
    with pytest.raises(KeyError):
        parent.permission_flags["can_community_read_files"]

    # test absence of a permission_flags field
    del parent["permission_flags"]
    permission_flags = parent.permission_flags
    assert permission_flags is None


def test_get_set_permission_flags_from_db(running_app, minimal_record, db):
    """Tests get and set of permission_flags from db."""
    parent_data = {"permission_flags": {"can_community_read_files": True}}
    parent = RDMParent.create(parent_data)
    record = RDMRecord.create(minimal_record, parent=parent)
    parent.commit()
    record.commit()
    db.session.commit()

    # test get from db
    db_record = RDMRecord.get_record(record.id)
    assert db_record.parent.permission_flags == {"can_community_read_files": True}

    # test remove flag
    parent.permission_flags = {}
    parent.commit()
    db.session.commit()

    db_record = RDMRecord.get_record(record.id)
    assert db_record.parent.permission_flags == {}


def test_cant_get_field_via_rest(running_app, minimal_record, service):
    """Tests that permission_flags is not accessible by REST api."""
    minimal_record["parent"] = {"permission_flags": {"can_community_read_files": True}}

    draft = service.create(system_identity, minimal_record)
    assert draft.to_dict()["errors"][0] == {
        "field": "parent.permission_flags",
        "messages": ["Unknown field."],
    }

    record = service.publish(system_identity, draft.id)
    result = service.read(system_identity, record.id)
    assert "permission_flags" not in result["parent"]
