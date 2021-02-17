# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the service AccessComponent."""

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
