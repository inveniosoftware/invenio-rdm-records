# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the service AccessComponent."""

from datetime import timedelta

import arrow
import pytest
from flask_principal import Identity, UserNeed
from marshmallow import ValidationError

from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.services import RDMRecordService
from invenio_rdm_records.services.components import AccessComponent


def test_access_component_valid(minimal_record, identity_simple):
    record = RDMRecord.create(minimal_record)
    component = AccessComponent(RDMRecordService())
    component.create(identity_simple, minimal_record, record)

    assert len(record.access.owners) == len(
        minimal_record["access"]["owned_by"]
    )


def test_access_component_unknown_owner(minimal_record, identity_simple):
    minimal_record["access"]["owned_by"] = [{"user": -1337}]

    record = RDMRecord.create(minimal_record)
    component = AccessComponent(RDMRecordService())

    with pytest.raises(ValidationError):
        component.create(identity_simple, minimal_record, record)

    with pytest.raises(ValidationError):
        component.update(identity_simple, minimal_record, record)


def test_access_component_unknown_grant_subject(
    minimal_record, identity_simple
):
    minimal_record["access"]["grants"] = [
        {"subject": "user", "id": "-1337", "level": "view"}
    ]

    record = RDMRecord.create(minimal_record)
    component = AccessComponent(RDMRecordService())

    with pytest.raises(ValidationError):
        component.create(identity_simple, minimal_record, record)

    with pytest.raises(ValidationError):
        component.update(identity_simple, minimal_record, record)


def test_access_component_set_owner(minimal_record, users):
    user = users[0]
    identity = Identity(user.id)
    identity.provides.add(UserNeed(user.id))

    minimal_record["access"]["owned_by"] = []

    # NOTE: we can't use RDMRecord.create(...) here, because
    #       the schema validation would complain about the zero-length
    #       owned_by array
    record = RDMRecord(minimal_record)
    component = AccessComponent(RDMRecordService())
    component.create(identity, minimal_record, record)

    assert len(record.access.owners) == 1
    assert list(record.access.owners)[0].resolve() == user


def test_access_component_update_access_via_json(
    minimal_record, users, identity_simple
):
    next_year = arrow.utcnow().datetime + timedelta(days=+365)
    restricted_access = {
        "owned_by": [{"user": users[0].id}],
        "grants": [],
        "record": "restricted",
        "files": "restricted",
        "embargo": {
            "until": next_year.strftime("%Y-%m-%d"),
            "active": True,
            "reason": "nothing in particular",
        },
    }
    minimal_record["access"] = restricted_access

    # create an initially restricted-access record
    record = RDMRecord.create(minimal_record)
    component = AccessComponent(RDMRecordService())
    component.create(identity_simple, minimal_record, record)

    prot = record.access.protection
    assert record.access.embargo is not None
    assert "embargo" in record["access"]
    assert prot.record == record["access"]["record"] == "restricted"
    assert prot.files == record["access"]["files"] == "restricted"

    # update the record's access via new json data
    # (instead of via the record's access object)
    new_data = minimal_record.copy()
    public_access = {
        "owned_by": [{"user": users[0].id}],
        "grants": [],
        "record": "public",
        "files": "public",
    }
    new_data["access"] = public_access
    component.create(identity_simple, new_data, record)

    prot = record.access.protection
    assert not record.access.embargo
    assert "embargo" not in record["access"]
    assert prot.record == record["access"]["record"] == "public"
    assert prot.files == record["access"]["files"] == "public"
