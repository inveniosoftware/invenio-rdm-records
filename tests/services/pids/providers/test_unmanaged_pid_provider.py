# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Unmanaged provider tests."""

import pytest
from flask_babelex import lazy_gettext as _
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from invenio_rdm_records.records import RDMDraft, RDMRecord
from invenio_rdm_records.services.pids.providers import UnmanagedPIDProvider


@pytest.fixture(scope="function")
def unmanaged_provider():
    """Application factory fixture."""
    return UnmanagedPIDProvider(pid_type="testid")


@pytest.fixture(scope="function")
def record(location):
    """Creates an empty record."""
    draft = RDMDraft.create({})
    record = RDMRecord.publish(draft)
    return record


def test_unmanaged_provider_create(record, unmanaged_provider):
    created_pid = unmanaged_provider.create(record, "avalue")
    db_pid = PersistentIdentifier.get(
        pid_value=created_pid.pid_value, pid_type="testid"
    )

    assert created_pid == db_pid
    assert created_pid.pid_value
    assert created_pid.pid_type == "testid"
    assert created_pid.status == PIDStatus.NEW


def test_unmanaged_provider_get(record, unmanaged_provider):
    created_pid = unmanaged_provider.create(record, "avalue")
    get_pid = unmanaged_provider.get(created_pid.pid_value)

    assert created_pid == get_pid
    assert get_pid.pid_value
    assert get_pid.pid_type == "testid"
    assert get_pid.status == PIDStatus.NEW


def test_unmanaged_provider_register(record, unmanaged_provider):
    created_pid = unmanaged_provider.create(record, "avalue")
    assert unmanaged_provider.register(pid=created_pid, record=record)

    db_pid = PersistentIdentifier.get(
        pid_value=created_pid.pid_value, pid_type="testid"
    )

    assert created_pid == db_pid
    assert db_pid.pid_value
    assert db_pid.pid_type == "testid"
    assert db_pid.status == PIDStatus.REGISTERED


def test_unmanaged_provider_validate(
    running_app, db, unmanaged_provider, record
):
    success, errors = unmanaged_provider.validate(
        record=record, provider="external"
    )
    assert success
    assert not errors


def test_unmanaged_provider_validate_failure(
    running_app, db, unmanaged_provider, record
):
    with pytest.raises(Exception):
        unmanaged_provider.validate(
            record=record, client="someclient", provider="external"
        )

    with pytest.raises(Exception):
        unmanaged_provider.validate(
            record=record, provider="wrong"
        )
