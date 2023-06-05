# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Records-Permissions is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

from typing import Pattern

import pytest
from flask_principal import Identity, UserNeed
from invenio_access.permissions import any_user, authenticated_user, system_process
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records_permissions.generators import (
    AnyUser,
    AuthenticatedUser,
    SystemProcess,
)

from invenio_rdm_records.records import RDMParent, RDMRecord
from invenio_rdm_records.services.generators import IfRestricted, RecordOwners


def _public_record():
    record = RDMRecord({}, access={})
    record.access.protection.set("public", "public")
    return record


def _restricted_record():
    record = RDMRecord({}, access={})
    record.access.protection.set("restricted", "restricted")
    return record


def _owned_record():
    parent = RDMParent.create({})
    parent.access.owner = {"user": 16}
    record = RDMRecord.create({}, parent=parent)
    return record


def _then_needs():
    return {authenticated_user, system_process}


def _else_needs():
    return {any_user, system_process}


#
# Tests
#
@pytest.mark.parametrize(
    "field,record_fun,expected_needs_fun",
    [
        ("record", _public_record, _else_needs),
        ("record", _restricted_record, _then_needs),
        ("files", _public_record, _else_needs),
        ("files", _restricted_record, _then_needs),
    ],
)
def test_ifrestricted_needs(field, record_fun, expected_needs_fun):
    """Test the IfRestricted generator."""
    generator = IfRestricted(
        field,
        then_=[AuthenticatedUser(), SystemProcess()],
        else_=[AnyUser(), SystemProcess()],
    )
    assert generator.needs(record=record_fun()) == expected_needs_fun()
    assert generator.excludes(record=record_fun()) == set()


def test_ifrestricted_query():
    """Test the query generation."""
    generator = IfRestricted("record", then_=[AuthenticatedUser()], else_=[AnyUser()])
    assert generator.query_filter(identity=any_user).to_dict() == {
        "bool": {
            "should": [
                {"match": {"access.record": "restricted"}},
                {"match": {"access.record": "public"}},
            ]
        }
    }


def test_record_owner(app, mocker):
    generator = RecordOwners()
    record = _owned_record()

    assert generator.needs(record=record) == [UserNeed(16)]

    assert generator.excludes(record=record) == []

    # Anonymous identity.
    assert not generator.query_filter(identity=mocker.Mock(provides=[]))

    # Authenticated identity
    query_filter = generator.query_filter(
        identity=mocker.Mock(provides=[mocker.Mock(method="id", value=15)])
    )

    expected_query_filter = {"terms": {"parent.access.owned_by.user": [15]}}
    assert query_filter.to_dict() == expected_query_filter
