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
from invenio_access.permissions import system_identity
from marshmallow import ValidationError

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.services.components import AccessComponent


def test_access_component_valid(
    minimal_record, parent, identity_simple, users
):
    record = RDMRecord.create(minimal_record, parent=parent)
    component = AccessComponent(current_rdm_records.records_service)
    component.create(identity_simple, minimal_record, record)

    assert len(record.parent.access.owners) > 0


# TODO this test doesn't currently make sense (the parents will handle owners)
@pytest.mark.skip
def test_access_component_unknown_owner(
    minimal_record, parent, identity_simple, users
):
    record = RDMRecord.create(minimal_record, parent=parent)
    record.parent["access"]["owned_by"] = [{"user": -1337}]
    component = AccessComponent(RDMRecordService())

    # both should work, since 'access.owned_by' is ignored for anybody
    # other than system processes
    component.create(identity_simple, minimal_record, record)
    component.update_draft(identity_simple, minimal_record, record)


# TODO this test doesn't currently make sense (the parents will handle owners)
@pytest.mark.skip
def test_access_component_unknown_owner_with_system_process(
    minimal_record, parent, users
):
    record = RDMRecord.create(minimal_record, parent=parent)
    record.parent["access"]["owned_by"] = [{"user": -1337}]
    component = AccessComponent(current_rdm_records.records_service)

    with pytest.raises(ValidationError):
        component.create(system_identity, minimal_record, record)

    with pytest.raises(ValidationError):
        component.update_draft(system_identity, minimal_record, record)


# TODO this test doesn't currently make sense (the parents will handle grants)
@pytest.mark.skip
def test_access_component_unknown_grant_subject(
    minimal_record, parent, identity_simple, users
):
    record = RDMRecord.create(minimal_record, parent=parent)
    record.parent["access"]["grants"] = [
        {"subject": "user", "id": "-1337", "level": "view"}
    ]
    component = AccessComponent(current_rdm_records.records_service)

    with pytest.raises(ValidationError):
        component.create(identity_simple, minimal_record, record)

    with pytest.raises(ValidationError):
        component.update_draft(identity_simple, minimal_record, record)


# TODO this test doesn't currently make sense (the parents will handle grants)
@pytest.mark.skip
def test_access_component_set_owner(minimal_record, parent, users):
    user = users[0]
    identity = Identity(user.id)
    identity.provides.add(UserNeed(user.id))

    record = RDMRecord.create(minimal_record, parent=parent)
    record.parent["access"]["owned_by"] = []
    component = AccessComponent(current_rdm_records.records_service)
    component.create(identity, minimal_record, record)

    assert len(record.access.owners) == 1
    assert list(record.access.owners)[0].resolve() == user


def test_access_component_update_access_via_json(
    minimal_record, parent, users, identity_simple
):
    next_year = arrow.utcnow().datetime + timedelta(days=+365)
    restricted_access = {
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
    record = RDMRecord.create(minimal_record, parent=parent)
    component = AccessComponent(current_rdm_records.records_service)
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
