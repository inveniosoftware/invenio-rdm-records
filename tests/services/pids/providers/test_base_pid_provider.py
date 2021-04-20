# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base provider tests."""

import pytest
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from invenio_rdm_records.services.pids.providers import BasePIDProvider


def test_base_provider_create(app, db):
    provider = BasePIDProvider()

    created_pid = provider.create(pid_value="1234", pid_type="testid")
    db_pid = PersistentIdentifier.get(pid_value="1234", pid_type="testid")

    assert created_pid == db_pid
    assert created_pid.pid_value == "1234"
    assert created_pid.pid_type == "testid"
    assert created_pid.status == PIDStatus.NEW


def test_base_provider_create_default_pid_type(app, db):
    provider = BasePIDProvider(pid_type="testid")

    created_pid = provider.create(pid_value="1234")
    # NOTE: DB level requires pid_type
    db_pid = PersistentIdentifier.get(pid_value="1234", pid_type="testid")

    assert created_pid == db_pid
    assert db_pid.pid_value == "1234"
    assert created_pid.pid_type == "testid"
    assert created_pid.status == PIDStatus.NEW


def test_base_provider_get_existing_different_pid_type(app, db):
    provider = BasePIDProvider(pid_type="testid")

    created_pid = provider.create(pid_value="1234", pid_type="diffid")
    get_pid = provider.get(pid_value="1234", pid_type="diffid")

    assert created_pid == get_pid
    assert get_pid.pid_value == "1234"
    assert get_pid.pid_type == "diffid"
    assert get_pid.status == PIDStatus.NEW


def test_base_provider_get_existing_different_status(app, db):
    provider = BasePIDProvider(pid_type="testid")

    created_pid = provider.create(pid_value="1234", status=PIDStatus.RESERVED)
    get_pid = provider.get(pid_value="1234")

    assert created_pid == get_pid
    assert get_pid.pid_value == "1234"
    assert get_pid.pid_type == "testid"
    assert get_pid.status == PIDStatus.RESERVED


def test_base_provider_reserve(app, db):
    provider = BasePIDProvider(pid_type="testid")

    created_pid = provider.create(pid_value="1234")
    assert provider.reserve(created_pid, {})

    # NOTE: DB level requires pid_type
    db_pid = PersistentIdentifier.get(pid_value="1234", pid_type="testid")

    assert db_pid.status == PIDStatus.RESERVED
    assert db_pid.pid_value == "1234"


def test_base_provider_register(app, db):
    provider = BasePIDProvider(pid_type="testid")

    created_pid = provider.create(pid_value="1234")
    assert provider.register(created_pid, {})

    # NOTE: DB level requires pid_type
    db_pid = PersistentIdentifier.get(pid_value="1234", pid_type="testid")

    assert db_pid.status == PIDStatus.REGISTERED
    assert db_pid.pid_value == "1234"


def test_base_provider_hard_delete(app, db):
    provider = BasePIDProvider(pid_type="testid")

    created_pid = provider.create(pid_value="1234")
    assert provider.delete(created_pid, {})

    # NOTE: DB level requires pid_type
    with pytest.raises(PIDDoesNotExistError):
        PersistentIdentifier.get(pid_value="1234", pid_type="testid")


def test_base_provider_soft_delete(app, db):
    provider = BasePIDProvider(pid_type="testid")

    created_pid = provider.create(pid_value="1234")
    assert provider.reserve(created_pid, {})
    assert provider.delete(created_pid, {})

    # NOTE: DB level requires pid_type
    db_pid = PersistentIdentifier.get(pid_value="1234", pid_type="testid")

    assert db_pid.status == PIDStatus.DELETED
    assert db_pid.pid_value == "1234"


def test_base_provider_get_status(app, db):
    provider = BasePIDProvider(pid_type="testid")

    created_pid = provider.create(pid_value="1234")
    assert provider.get_status(created_pid.pid_value) == PIDStatus.NEW


def test_base_provider_validate(app, db):
    provider = BasePIDProvider(pid_type="testid")
    # NOTE: BasePIDProvider defaults name to None
    assert provider.validate(identifier=None, client=None, provider=None)
