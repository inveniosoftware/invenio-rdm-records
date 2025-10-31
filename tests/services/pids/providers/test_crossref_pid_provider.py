# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2023 Northwestern University.
# Copyright (C) 2025 Front Matter.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Crossref provider tests."""

import pytest
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records import RDMDraft, RDMRecord
from invenio_rdm_records.services.pids.providers import (
    CrossrefClient,
    CrossrefPIDProvider,
)


@pytest.fixture()
def crossref_provider(mocker):
    mocker.patch(
        "invenio_rdm_records.services.pids.providers.crossref.CrossrefXMLClient"
    )

    return CrossrefPIDProvider("crossref", client=CrossrefClient("crossref"))


@pytest.fixture(scope="function")
def record(location):
    """Creates an empty record."""
    draft = RDMDraft.create({})
    record = RDMRecord.publish(draft)

    return record


@pytest.fixture(scope="function")
def record_w_links(running_app, minimal_record):
    """Creates an empty record."""
    service = current_rdm_records.records_service
    draft = service.create(system_identity, minimal_record)
    record = service.publish(system_identity, draft.id)

    return record.to_dict()


def test_crossref_provider_create(record, crossref_provider):
    created_pid = crossref_provider.create(record)
    db_pid = PersistentIdentifier.get(pid_value=created_pid.pid_value, pid_type="doi")

    assert created_pid == db_pid
    assert created_pid.pid_value
    assert created_pid.pid_type == "doi"
    assert created_pid.status == PIDStatus.NEW


def test_crossref_provider_get(record, crossref_provider):
    created_pid = crossref_provider.create(record)
    get_pid = crossref_provider.get(created_pid.pid_value)

    assert created_pid == get_pid
    assert get_pid.pid_value
    assert get_pid.pid_type == "doi"
    assert get_pid.status == PIDStatus.NEW


def test_crossref_provider_reserve(record, crossref_provider):
    created_pid = crossref_provider.create(record)
    assert crossref_provider.reserve(pid=created_pid, record=record)

    db_pid = PersistentIdentifier.get(pid_value=created_pid.pid_value, pid_type="doi")

    assert created_pid == db_pid
    assert db_pid.pid_value
    assert db_pid.pid_type == "doi"
    assert db_pid.status == PIDStatus.RESERVED


def test_crossref_provider_register(record_w_links, crossref_provider, mocker):
    mocker.patch(
        "invenio_rdm_records.services.pids.providers.crossref."
        + "CrossrefXMLSerializer"
    )
    created_pid = crossref_provider.get(record_w_links["pids"]["doi"]["identifier"])
    assert crossref_provider.register(
        pid=created_pid,
        record=record_w_links,
        url=record_w_links["links"]["self_html"],
    )

    db_pid = PersistentIdentifier.get(pid_value=created_pid.pid_value, pid_type="doi")

    assert created_pid == db_pid
    assert db_pid.pid_value
    assert db_pid.pid_type == "doi"
    assert db_pid.status == PIDStatus.REGISTERED


def test_crossref_provider_update(record_w_links, crossref_provider, mocker):
    mocker.patch(
        "invenio_rdm_records.services.pids.providers.crossref."
        + "CrossrefXMLSerializer"
    )
    created_pid = crossref_provider.get(record_w_links["pids"]["doi"]["identifier"])
    assert crossref_provider.register(
        pid=created_pid, record=record_w_links, url=record_w_links["links"]["self_html"]
    )
    assert crossref_provider.update(pid=created_pid, record=record_w_links, url=None)

    db_pid = PersistentIdentifier.get(pid_value=created_pid.pid_value, pid_type="doi")

    assert created_pid == db_pid
    assert db_pid.pid_value
    assert db_pid.pid_type == "doi"
    assert db_pid.status == PIDStatus.REGISTERED


def test_crossref_provider_unregister_new(record, crossref_provider):
    # Unregister NEW is a hard delete
    created_pid = crossref_provider.create(record)
    assert created_pid.status == PIDStatus.NEW
    assert crossref_provider.delete(created_pid)

    with pytest.raises(PIDDoesNotExistError):
        PersistentIdentifier.get(pid_value=created_pid.pid_value, pid_type="doi")


def test_crossref_provider_unregister_reserved(record, crossref_provider):
    # Unregister NEW is a soft delete
    created_pid = crossref_provider.create(record)
    assert crossref_provider.reserve(pid=created_pid, record=record)
    assert created_pid.status == PIDStatus.RESERVED
    assert crossref_provider.delete(created_pid)

    # reserve keeps status as RESERVED so is soft deleted
    pid = PersistentIdentifier.get(pid_value=created_pid.pid_value, pid_type="doi")
    assert pid.status == PIDStatus.DELETED


def test_crossref_provider_unregister_registered(
    record_w_links, crossref_provider, mocker
):
    mocker.patch(
        "invenio_rdm_records.services.pids.providers.crossref."
        + "CrossrefXMLSerializer"
    )
    # Unregister NEW is a soft delete
    created_pid = crossref_provider.get(record_w_links["pids"]["doi"]["identifier"])
    assert crossref_provider.register(
        pid=created_pid, record=record_w_links, url=record_w_links["links"]["self_html"]
    )
    assert created_pid.status == PIDStatus.REGISTERED
    assert crossref_provider.delete(created_pid)

    deleted_pid = PersistentIdentifier.get(
        pid_value=created_pid.pid_value, pid_type="doi"
    )
    assert deleted_pid.status == PIDStatus.DELETED


def test_crossref_provider_configuration(record, mocker):
    def custom_format_func(*args):
        return "10.123/custom.func"

    client = CrossrefClient("crossref")

    # check with default func
    crossref_provider = CrossrefPIDProvider("crossref", client=client)
    expected_result = crossref_provider.generate_id(record)
    assert crossref_provider.create(record).pid_value == expected_result

    # check id generation from env func
    current_app.config["CROSSREF_FORMAT"] = custom_format_func
    crossref_provider = CrossrefPIDProvider("crossref", client=client)
    assert crossref_provider.create(record).pid_value == "10.123/custom.func"

    # check id generation from env f-string
    current_app.config["CROSSREF_FORMAT"] = "{prefix}/crossref2.{id}"  # noqa
    crossref_provider = CrossrefPIDProvider("crossref", client=client)
    expected_result = crossref_provider.generate_id(record)
    assert crossref_provider.create(record).pid_value == expected_result


def test_crossref_provider_validation(record):
    current_app.config["CROSSREF_PREFIX"] = "10.1000"
    client = CrossrefClient("crossref")
    crossref_provider = CrossrefPIDProvider("crossref", client=client)
    record["metadata"] = {"publisher": "Acme Inc"}

    # Case - Valid identifier (doi) + record
    success, errors = crossref_provider.validate(
        record=record, identifier="10.1000/valid.1234", provider="crossref"
    )
    assert success
    assert [] == errors

    # Case - Invalid identifier (doi)
    success, errors = crossref_provider.validate(
        record=record, identifier="10.2000/invalid.1234", provider="crossref"
    )
    assert not success
    expected = [
        {
            "field": "pids.doi",
            "messages": [
                "Wrong DOI 10.2000 prefix provided, "
                + "it should be 10.1000 as defined in the rest client"
            ],
        }
    ]
    assert expected == errors

    current_app.config["CROSSREF_PREFIX"] = "10.1000"
    client = CrossrefClient("crossref")
    crossref_provider = CrossrefPIDProvider("crossref", client=client)

    # Case - valid new record without pids.doi (empty pid_dict)
    assert not record.get("pids", {}).get("doi")
    success, errors = crossref_provider.validate(record=record, **{})
    assert [] == errors
    assert success

    # Case - invalid record
    del record["metadata"]["publisher"]
    success, errors = crossref_provider.validate(
        record=record, identifier="10.1000/valid.1234", provider="crossref"
    )
    expected = [
        {
            "field": "metadata.publisher",
            "messages": ["Missing publisher field required for DOI registration."],
        }
    ]
    assert expected == errors
    assert not success
