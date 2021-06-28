# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base provider tests."""

import pytest
from flask_babelex import lazy_gettext as _
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from invenio_rdm_records.services.pids.providers import BasePIDProvider


def test_base_provider_create(app, db):
    provider = BasePIDProvider()

    created_pid = provider.create_by_pid(pid_value="1234", pid_type="testid")
    db_pid = PersistentIdentifier.get(pid_value="1234", pid_type="testid")

    assert created_pid == db_pid
    assert created_pid.pid_value == "1234"
    assert created_pid.pid_type == "testid"
    assert created_pid.status == PIDStatus.NEW


@pytest.fixture(scope='function')
def base_provider():
    """Application factory fixture."""
    return BasePIDProvider(pid_type="testid")


def test_base_provider_create_default_pid_type(app, db, base_provider):
    provider = base_provider
    created_pid = provider.create_by_pid(pid_value="1234")
    # NOTE: DB level requires pid_type
    db_pid = PersistentIdentifier.get(pid_value="1234", pid_type="testid")

    assert created_pid == db_pid
    assert db_pid.pid_value == "1234"
    assert created_pid.pid_type == "testid"
    assert created_pid.status == PIDStatus.NEW


def test_base_provider_get_existing_different_pid_type(
    app, db, base_provider
):
    provider = base_provider

    created_pid = provider.create_by_pid(pid_value="1234", pid_type="diffid")
    get_pid = provider.get(pid_value="1234", pid_type="diffid")

    assert created_pid == get_pid
    assert get_pid.pid_value == "1234"
    assert get_pid.pid_type == "diffid"
    assert get_pid.status == PIDStatus.NEW


def test_base_provider_get_existing_different_status(
    app, db, base_provider
):
    provider = base_provider

    created_pid = provider.create_by_pid(pid_value="1234",
                                         status=PIDStatus.RESERVED)
    get_pid = provider.get(pid_value="1234")

    assert created_pid == get_pid
    assert get_pid.pid_value == "1234"
    assert get_pid.pid_type == "testid"
    assert get_pid.status == PIDStatus.RESERVED


def test_base_provider_reserve(app, db, base_provider):
    provider = base_provider

    created_pid = provider.create_by_pid(pid_value="1234")
    assert provider.reserve(created_pid, {})

    # NOTE: DB level requires pid_type
    db_pid = PersistentIdentifier.get(pid_value="1234", pid_type="testid")

    assert db_pid.status == PIDStatus.RESERVED
    assert db_pid.pid_value == "1234"


def test_base_provider_register(app, db, base_provider):
    provider = base_provider

    created_pid = provider.create_by_pid(pid_value="1234")
    assert provider.register(created_pid, {})

    # NOTE: DB level requires pid_type
    db_pid = PersistentIdentifier.get(pid_value="1234", pid_type="testid")

    assert db_pid.status == PIDStatus.REGISTERED
    assert db_pid.pid_value == "1234"


def test_base_provider_hard_delete(app, db, base_provider):
    provider = base_provider

    created_pid = provider.create_by_pid(pid_value="1234")
    assert provider.delete(created_pid, {})

    # NOTE: DB level requires pid_type
    with pytest.raises(PIDDoesNotExistError):
        PersistentIdentifier.get(pid_value="1234", pid_type="testid")


def test_base_provider_soft_delete(app, db, base_provider):
    provider = base_provider

    created_pid = provider.create_by_pid(pid_value="1234")
    assert provider.reserve(created_pid, {})
    assert provider.delete(created_pid, {})

    # NOTE: DB level requires pid_type
    db_pid = PersistentIdentifier.get(pid_value="1234", pid_type="testid")

    assert db_pid.status == PIDStatus.DELETED
    assert db_pid.pid_value == "1234"


def test_base_provider_get_status(app, db, base_provider):
    provider = base_provider

    created_pid = provider.create_by_pid(pid_value="1234")
    assert provider.get_status(created_pid.pid_value) == PIDStatus.NEW


def test_base_provider_validate_no_values_given(
    running_app, db, base_provider, record
):
    provider = base_provider
    # base has name set to None
    success, errors = provider.validate(
        record=record, identifier=None, client=None, provider=None)
    assert success
    assert not errors


def test_base_provider_validate_failure(
    running_app, db, base_provider, record
):
    provider = base_provider
    with pytest.raises(Exception):
        provider.validate(
            record=record, identifier=None, client=None, provider="fail")
