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

from invenio_rdm_records.records import RDMDraft, RDMRecord
from invenio_rdm_records.services.pids.providers import DOIDataCitePIDProvider


@pytest.fixture()
def datacite_provider(mocker):
    client = mocker.patch(
        "invenio_rdm_records.services.pids.providers.datacite."
        "DOIDataCiteClient")
    mocker.patch("invenio_rdm_records.services.pids.providers.datacite." +
                 "DataCiteRESTClient")

    return DOIDataCitePIDProvider(name="datacite", client=client)


@pytest.fixture(scope="function")
def record(location):
    """Creates an empty record."""
    draft = RDMDraft.create({})
    record = RDMRecord.publish(draft)

    return record


def test_datacite_provider_create(record, datacite_provider):

    created_pid = datacite_provider.create(record)
    db_pid = PersistentIdentifier.get(
        pid_value=created_pid.pid_value, pid_type="doi")

    assert created_pid == db_pid
    assert created_pid.pid_value
    assert created_pid.pid_type == "doi"
    assert created_pid.status == PIDStatus.NEW


def test_datacite_provider_get(record, datacite_provider):
    created_pid = datacite_provider.create(record)
    get_pid = datacite_provider.get(created_pid.pid_value)

    assert created_pid == get_pid
    assert get_pid.pid_value
    assert get_pid.pid_type == "doi"
    assert get_pid.status == PIDStatus.NEW


def test_datacite_provider_reserve(record, datacite_provider):
    created_pid = datacite_provider.create(record)
    assert datacite_provider.reserve(pid=created_pid, record=record)

    db_pid = PersistentIdentifier.get(
        pid_value=created_pid.pid_value, pid_type="doi")

    assert created_pid == db_pid
    assert db_pid.pid_value
    assert db_pid.pid_type == "doi"
    assert db_pid.status == PIDStatus.NEW


def test_datacite_provider_register(record, datacite_provider, mocker):
    mocker.patch("invenio_rdm_records.services.pids.providers.datacite." +
                 "DataCite43JSONSerializer")
    created_pid = datacite_provider.create(record)
    assert datacite_provider.register(pid=created_pid, record=record, url=None)

    db_pid = PersistentIdentifier.get(
        pid_value=created_pid.pid_value, pid_type="doi")

    assert created_pid == db_pid
    assert db_pid.pid_value
    assert db_pid.pid_type == "doi"
    assert db_pid.status == PIDStatus.REGISTERED


def test_datacite_provider_update(record, datacite_provider, mocker):
    mocker.patch("invenio_rdm_records.services.pids.providers.datacite." +
                 "DataCite43JSONSerializer")
    created_pid = datacite_provider.create(record)
    assert datacite_provider.register(
        pid=created_pid, record=record, url=None)
    assert datacite_provider.update(pid=created_pid, record=record, url=None)

    db_pid = PersistentIdentifier.get(
        pid_value=created_pid.pid_value, pid_type="doi")

    assert created_pid == db_pid
    assert db_pid.pid_value
    assert db_pid.pid_type == "doi"
    assert db_pid.status == PIDStatus.REGISTERED


def test_datacite_provider_unregister_new(record, datacite_provider):
    # Unregister NEW is a hard delete
    created_pid = datacite_provider.create(record)
    assert created_pid.status == PIDStatus.NEW
    assert datacite_provider.delete(created_pid, record)

    with pytest.raises(PIDDoesNotExistError):
        PersistentIdentifier.get(
            pid_value=created_pid.pid_value, pid_type="doi")


def test_datacite_provider_unregister_reserved(
    record, datacite_provider
):
    # Unregister NEW is a soft delete
    created_pid = datacite_provider.create(record)
    assert datacite_provider.reserve(pid=created_pid, record=record)
    assert created_pid.status == PIDStatus.NEW
    assert datacite_provider.delete(created_pid, record)

    # reserve keeps status as NEW so is hard deleted
    with pytest.raises(PIDDoesNotExistError):
        PersistentIdentifier.get(
            pid_value=created_pid.pid_value, pid_type="doi")


def test_datacite_provider_unregister_regitered(
    record, datacite_provider, mocker
):
    mocker.patch("invenio_rdm_records.services.pids.providers.datacite." +
                 "DataCite43JSONSerializer")
    # Unregister NEW is a soft delete
    created_pid = datacite_provider.create(record)
    assert datacite_provider.register(pid=created_pid, record=record, url=None)
    assert created_pid.status == PIDStatus.REGISTERED
    assert datacite_provider.delete(created_pid, record)

    deleted_pid = PersistentIdentifier.get(
            pid_value=created_pid.pid_value, pid_type="doi")
    assert deleted_pid.status == PIDStatus.DELETED


def test_datacite_provider_get_status(record, datacite_provider):
    created_pid = datacite_provider.create(record)
    status = datacite_provider.get_status(created_pid.pid_value)
    assert status == PIDStatus.NEW
