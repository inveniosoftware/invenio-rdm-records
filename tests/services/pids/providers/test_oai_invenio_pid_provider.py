# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite invenio_provider tests."""

import pytest
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from invenio_rdm_records.records import RDMDraft, RDMRecord
from invenio_rdm_records.services.pids.providers import OAIPIDProvider


@pytest.fixture()
def invenio_provider(mocker):
    return OAIPIDProvider("oai")


@pytest.fixture(scope="function")
def record(location):
    """Creates an empty record."""
    draft = RDMDraft.create({})
    record = RDMRecord.publish(draft)

    return record


def test_invenio_provider_create(record, invenio_provider):
    created_pid = invenio_provider.create(record)
    db_pid = PersistentIdentifier.get(pid_value=created_pid.pid_value, pid_type="oai")

    assert created_pid == db_pid
    assert created_pid.pid_value
    assert created_pid.pid_value == db_pid.pid_value
    assert created_pid.pid_type == "oai"
    assert created_pid.status == PIDStatus.REGISTERED


def test_invenio_provider_get(record, invenio_provider):
    created_pid = invenio_provider.create(record)
    get_pid = invenio_provider.get(created_pid.pid_value)

    assert created_pid == get_pid
    assert get_pid.pid_value
    assert get_pid.pid_type == "oai"
    assert get_pid.status == PIDStatus.REGISTERED


def test_invenio_provider_reserve(record, invenio_provider):
    created_pid = invenio_provider.create(record)
    assert invenio_provider.reserve(pid=created_pid, record=record)

    db_pid = PersistentIdentifier.get(pid_value=created_pid.pid_value, pid_type="oai")

    assert created_pid == db_pid
    assert db_pid.pid_value
    assert db_pid.pid_type == "oai"
    assert db_pid.status == PIDStatus.REGISTERED
