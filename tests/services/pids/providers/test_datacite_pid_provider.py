# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite datacite_provider tests."""

import pytest
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from invenio_rdm_records.services.pids.providers import DataCiteClient, \
    DataCitePIDProvider


@pytest.fixture()
def datacite_provider():

    return DataCitePIDProvider(
        name="datacite", client=DataCiteClient(name="inveniordm"))


# PIDS-FIXME: Need to test querying Datacite API
def test_datacite_datacite_provider_create(app, db, datacite_provider):
    created_pid = datacite_provider.create(recid="12345-abcde")
    db_pid = PersistentIdentifier.get(
        pid_value=created_pid.pid_value, pid_type="doi")

    assert created_pid == db_pid
    assert created_pid.pid_value
    assert created_pid.pid_type == "doi"
    assert created_pid.status == PIDStatus.NEW


def test_datacite_provider_get(app, db, datacite_provider):
    created_pid = datacite_provider.create(recid="12345-abcde")
    get_pid = datacite_provider.get(created_pid.pid_value)

    assert created_pid == get_pid
    assert get_pid.pid_value
    assert get_pid.pid_type == "doi"
    assert get_pid.status == PIDStatus.NEW


def test_datacite_provider_reserve(app, db, datacite_provider):
    created_pid = datacite_provider.create(recid="12345-abcde")
    assert datacite_provider.reserve(pid=created_pid, record=None)

    db_pid = PersistentIdentifier.get(
        pid_value=created_pid.pid_value, pid_type="doi")

    assert created_pid == db_pid
    assert db_pid.pid_value
    assert db_pid.pid_type == "doi"
    assert db_pid.status == PIDStatus.RESERVED


def test_datacite_provider_register(app, db, datacite_provider):
    created_pid = datacite_provider.create(recid="12345-abcde")
    assert datacite_provider.register(pid=created_pid, record=None)

    db_pid = PersistentIdentifier.get(
        pid_value=created_pid.pid_value, pid_type="doi")

    assert created_pid == db_pid
    assert db_pid.pid_value
    assert db_pid.pid_type == "doi"
    assert db_pid.status == PIDStatus.REGISTERED


def test_datacite_provider_update(app, db, datacite_provider):
    created_pid = datacite_provider.create(recid="12345-abcde")
    assert datacite_provider.register(pid=created_pid, record=None)
    assert datacite_provider.updated(pid=created_pid, record=None)

    db_pid = PersistentIdentifier.get(
        pid_value=created_pid.pid_value, pid_type="doi")

    assert created_pid == db_pid
    assert db_pid.pid_value
    assert db_pid.pid_type == "doi"
    assert db_pid.status == PIDStatus.REGISTERED


def test_datacite_provider_unregister_new(app, db, datacite_provider):
    # Unregister NEW is a hard delete
    created_pid = datacite_provider.create(recid="12345-abcde")
    assert created_pid.status == PIDStatus.NEW
    assert datacite_provider.delete(created_pid)

    with pytest.raises(PIDDoesNotExistError):
        PersistentIdentifier.get(
            pid_value=created_pid.pid_value, pid_type="doi")


def test_datacite_provider_unregister_reserved(
        app, db, datacite_provider):
    # Unregister NEW is a soft delete
    created_pid = datacite_provider.create(recid="12345-abcde")
    assert datacite_provider.reserve(pid=created_pid, record=None)
    assert created_pid.status == PIDStatus.RESERVED
    assert datacite_provider.delete(created_pid)

    with pytest.raises(PIDDoesNotExistError):
        PersistentIdentifier.get(
            pid_value=created_pid.pid_value, pid_type="doi")


def test_datacite_provider_unregister_regitered(
        app, db, datacite_provider):
    # Unregister NEW is a soft delete
    created_pid = datacite_provider.create(recid="12345-abcde")
    assert datacite_provider.register(pid=created_pid, record=None)
    assert created_pid.status == PIDStatus.REGISTERED
    assert datacite_provider.delete(created_pid)

    with pytest.raises(PIDDoesNotExistError):
        PersistentIdentifier.get(
            pid_value=created_pid.pid_value, pid_type="doi")


def test_datacite_provider_get_status(app, db, datacite_provider):
    created_pid = datacite_provider.create(pid_value="rdm.1234567")
    status = datacite_provider.get_status(created_pid.pid_value)
    assert status == PIDStatus.NEW


def test_datacite_provider_validate(app, db, datacite_provider):
    pass
