# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the service ExternalPIDsComponent."""

import pytest
from invenio_db import db
from marshmallow import ValidationError

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records import RDMDraft, RDMRecord
from invenio_rdm_records.services import RDMRecordService
from invenio_rdm_records.services.components import ExternalPIDsComponent
from invenio_rdm_records.services.config import RDMRecordServiceConfig
from invenio_rdm_records.services.pids.providers import DOIDataCiteClient, \
    DOIDataCitePIDProvider, UnmanagedPIDProvider

#
# Unmanaged Provider
#


class RequiredUnmanagedPIDProvider(UnmanagedPIDProvider):
    """Custom unmanaged PID provider."""

    name = "requman"


class NotRequiredUnmanagedPIDProvider(UnmanagedPIDProvider):
    """Custom unmanaged PID provider."""

    name = "nrequman"


class TestServiceReqUnmanConfig(RDMRecordServiceConfig):
    """Custom service config with only pid providers."""
    pids_providers = {
        "requman": {  # Required Unmanaged
            "requman": {
                "provider": RequiredUnmanagedPIDProvider,
                "required": True,
                "system_managed": False,
            }
        }
    }

    pids_providers_clients = {}


class TestServiceNReqUnmanConfig(RDMRecordServiceConfig):
    """Custom service config with only pid providers."""
    pids_providers = {
        "nrequman": {  # Non required Unmanaged
            "nrequman": {
                "provider": NotRequiredUnmanagedPIDProvider,
                "required": False,
                "system_managed": False,
            }
        }
    }

    pids_providers_clients = {}


@pytest.fixture(scope="function")
def req_pid_unmanaged_cmp():
    service = RDMRecordService(config=TestServiceReqUnmanConfig())

    return ExternalPIDsComponent(service=service)


@pytest.fixture(scope="function")
def not_req_unmanaged_pid_cmp():
    service = RDMRecordService(config=TestServiceNReqUnmanConfig())

    return ExternalPIDsComponent(service=service)


def test_unmanaged_required_pid_value(
    req_pid_unmanaged_cmp, minimal_record, identity_simple, location
):
    component = req_pid_unmanaged_cmp
    pids = {
        "requman": {
            "identifier": "value",
            "provider": "requman",
        }
    }

    # make sure `pids` field is added
    data = minimal_record.copy()
    data["pids"] = pids

    # create a minimal draft
    draft = RDMDraft.create(data)
    component.create(identity_simple, data=data, record=draft)
    assert "pids" in draft and draft.pids == pids

    # publish
    record = RDMRecord.publish(draft)
    component.publish(identity_simple, draft=draft, record=record)
    assert record.pids == pids


def test_unmanaged_required_no_pid_value(
    req_pid_unmanaged_cmp, minimal_record, identity_simple, location
):
    component = req_pid_unmanaged_cmp
    pids = {
        "requman": {
            "provider": "requman",
        }
    }

    # make sure `pids` field is added
    data = minimal_record.copy()
    data["pids"] = pids

    # create a minimal draft
    draft = RDMDraft.create(data)
    component.create(identity_simple, data=data, record=draft)
    assert "pids" in draft and draft.pids == pids

    # publish, fail because is required an no value given
    record = RDMRecord.publish(draft)
    with pytest.raises(ValidationError):
        component.publish(identity_simple, draft=draft, record=record)


def test_unmanaged_no_required_pid_value(
    not_req_unmanaged_pid_cmp, minimal_record, identity_simple, location
):
    component = not_req_unmanaged_pid_cmp
    pids = {
        "nrequman": {
            "identifier": "value",
            "provider": "nrequman",
        }
    }

    # make sure `pids` field is added
    data = minimal_record.copy()
    data["pids"] = pids

    # create a minimal draft
    draft = RDMDraft.create(data)
    component.create(identity_simple, data=data, record=draft)
    assert "pids" in draft and draft.pids == pids
    # publish
    record = RDMRecord.publish(draft)
    component.publish(identity_simple, draft=draft, record=record)
    assert record.pids == pids


def test_unmanaged_no_required_no_partial_value(
    not_req_unmanaged_pid_cmp, minimal_record, identity_simple, location
):
    component = not_req_unmanaged_pid_cmp
    pids = {
        "nrequman": {
            "provider": "nrequman",
        }
    }

    # make sure `pids` field is added
    data = minimal_record.copy()
    data["pids"] = pids

    # create a minimal draft
    draft = RDMDraft.create(data)
    component.create(identity_simple, data=data, record=draft)
    assert "pids" in draft and draft.pids == pids

    # publish
    # NOTE: Better fail than strip and not tell the user.
    record = RDMRecord.publish(draft)
    with pytest.raises(ValidationError):
        component.publish(identity_simple, draft=draft, record=record)


def test_unmanaged_no_required_no_value(
    not_req_unmanaged_pid_cmp, minimal_record, identity_simple, location
):
    # NOTE: Since is {} should simply be ignored
    component = not_req_unmanaged_pid_cmp
    pids = {
        "nrequman": {}
    }

    # make sure `pids` field is added
    data = minimal_record.copy()
    data["pids"] = pids

    # create a minimal draft
    draft = RDMDraft.create(data)
    component.create(identity_simple, data=data, record=draft)
    assert "pids" in draft and draft.pids == pids

    # publish
    record = RDMRecord.publish(draft)
    component.publish(identity_simple, draft=draft, record=record)


def test_unmanaged_no_required_no_pids(
    not_req_unmanaged_pid_cmp, minimal_record, identity_simple, location
):
    # NOTE: Since is {} should simply be ignored
    component = not_req_unmanaged_pid_cmp
    pids = {}

    # make sure `pids` field is added
    data = minimal_record.copy()
    data["pids"] = pids

    # create a minimal draft
    draft = RDMDraft.create(data)
    component.create(identity_simple, data=data, record=draft)
    assert "pids" in draft and draft.pids == pids

    # publish
    record = RDMRecord.publish(draft)
    component.publish(identity_simple, draft=draft, record=record)


#
# Managed Provider, using DOI as an example
#
class TestServiceNReqManConfig(RDMRecordServiceConfig):
    """Custom service config with only pid providers."""
    pids_providers = {
        "doi": {
            "datacite": {
                "provider": DOIDataCitePIDProvider,
                "required": False,
                "system_managed": True,
            }
        },
    }

    pids_providers_clients = {
        "datacite": DOIDataCiteClient,  # default for when no client is passed
        "rdm": DOIDataCiteClient
    }


class TestServiceReqManConfig(TestServiceNReqManConfig):
    """Custom service config with only pid providers."""
    pids_providers = {
        "doi": {
            "datacite": {
                "provider": DOIDataCitePIDProvider,
                "required": True,
                "system_managed": True,
            }
        },
    }


@pytest.fixture(scope="function")
def not_req_managed_pid_cmp():
    service = RDMRecordService(config=TestServiceNReqManConfig())

    return ExternalPIDsComponent(service=service)


@pytest.fixture(scope="function")
def req_managed_pid_cmp():
    service = RDMRecordService(config=TestServiceReqManConfig())

    return ExternalPIDsComponent(service=service)


def test_non_configured_provider(
    not_req_managed_pid_cmp, minimal_record, identity_simple, location
):
    component = not_req_managed_pid_cmp
    pids = {
        "noconfig": {
            "provider": "nrequman",
        }
    }

    # make sure `pids` field is added
    data = minimal_record.copy()
    data["pids"] = pids

    # create a minimal draft
    draft = RDMDraft.create(data)
    with pytest.raises(ValidationError):
        component.create(identity_simple, data=data, record=draft)


def test_create_managed_doi_empty_pids(
    req_managed_pid_cmp, minimal_record, identity_simple, mocker, location
):
    mocker.patch("invenio_rdm_records.services.config.DOIDataCiteClient")
    mocker.patch("invenio_rdm_records.services.pids.providers.datacite." +
                 "DataCiteRESTClient")
    component = req_managed_pid_cmp
    pids = {}

    # make sure `pids` field is added
    data = minimal_record.copy()
    data["pids"] = pids

    # create a minimal draft
    draft = RDMDraft.create(data)
    component.create(identity_simple, data=data, record=draft)
    assert "pids" in draft and draft.pids == pids

    # publish
    record = RDMRecord.publish(draft)
    component.publish(identity_simple, draft=draft, record=record)
    doi = record.pids.get("doi")

    assert doi
    assert doi.get("identifier")
    assert doi["provider"] == "datacite"
    assert doi["client"] == "datacite"  # default


def test_create_managed_doi_with_no_value(
    req_managed_pid_cmp, minimal_record, identity_simple, mocker, location
):
    mocker.patch("invenio_rdm_records.services.pids.providers.datacite." +
                 "DataCiteRESTClient")
    mocker.patch("invenio_rdm_records.services.pids.providers.datacite." +
                 "DataCite43JSONSerializer")
    component = req_managed_pid_cmp
    pids = {
        "doi": {
            "provider": "datacite",
            "client": "rdm"
        }
    }

    # make sure `pids` field is added
    data = minimal_record.copy()
    data["pids"] = pids

    # create a minimal draft
    draft = RDMDraft.create(data)
    component.create(identity_simple, data=data, record=draft)
    assert "pids" in draft and draft.pids == pids
    # publish
    record = RDMRecord.publish(draft)
    component.publish(identity_simple, draft=draft, record=record)
    doi = record.pids.get("doi")
    assert doi
    assert doi.get("identifier")
    assert doi["provider"] == "datacite"
    assert doi["client"] == "rdm"  # tests non-default client works


def test_create_managed_doi_with_value(
    req_managed_pid_cmp, minimal_record, identity_simple, mocker, location
):
    client = mocker.patch(
        "invenio_rdm_records.services.pids.providers.datacite."
        "DOIDataCiteClient")
    mocker.patch("invenio_rdm_records.services.pids.providers.datacite." +
                 "DataCiteRESTClient")
    component = req_managed_pid_cmp

    # create a minimal draft
    data = minimal_record.copy()
    draft = RDMDraft.create(data)
    component.create(identity_simple, data=data, record=draft)
    assert "pids" in draft and draft.pids == {}

    # when provider is managed and required, and the identifier is in the
    # payload, it means that it was reserved via the `reserve` endpoint
    provider = DOIDataCitePIDProvider(client)
    pid = provider.create(draft)
    provider.reserve(pid, draft)
    db.session.commit()

    pids = {
        "doi": {
            "identifier": pid.pid_value,
            "provider": "datacite",
            "client": "rdm"
        }
    }
    draft["pids"] = pids

    # publish
    record = RDMRecord.publish(draft)
    component.publish(identity_simple, draft=draft, record=record)
    assert record.pids == pids

    assert provider.get(pid.pid_value).is_registered()


#
#  DOI / Versioning
#
def test_doi_publish_versions(
    app, location, minimal_record, identity_simple, mocker
):
    client = mocker.patch(
        "invenio_rdm_records.services.pids.providers.datacite."
        "DOIDataCiteClient")
    mocker.patch("invenio_rdm_records.services.pids.providers.datacite." +
                 "DataCiteRESTClient")
    mocker.patch("invenio_rdm_records.services.pids.providers.datacite." +
                 "DataCite43JSONSerializer")
    component = ExternalPIDsComponent(current_rdm_records.records_service)
    doi_provider = DOIDataCitePIDProvider(client)

    data = minimal_record.copy()
    # make sure `pids` field is added on create
    del data["pids"]

    # create a minimal draft
    draft = RDMDraft.create(data)
    component.create(identity_simple, data=data, record=draft)
    assert "pids" in draft and draft.pids == {}

    # publish
    record = RDMRecord.publish(draft)
    # NOTE: simulate metadata component required by datacite serialization
    record["metadata"] = draft["metadata"]
    component.publish(identity_simple, draft=draft, record=record)
    doi_v1 = record.pids["doi"]
    # DOI
    assert doi_v1
    assert doi_v1["identifier"]
    assert doi_v1["provider"] == "datacite"
    assert doi_v1["client"] == "datacite"  # Default since no values given

    doi_pid = doi_provider.get(doi_v1["identifier"])
    assert doi_pid.object_uuid == record.id

    # create a new version (v2) of the record
    draft_v2 = RDMDraft.new_version(record)
    component.new_version(identity_simple, draft=draft_v2, record=record)
    assert "pids" in draft and draft.pids == {}

    # publish v2
    record_v2 = RDMRecord.publish(draft_v2)
    # NOTE: simulate metadata component required by datacite serialization
    draft_v2["metadata"] = minimal_record["metadata"]
    component.publish(identity_simple, draft=draft_v2, record=record_v2)
    doi_v2 = record_v2.pids["doi"]
    # DOI
    assert doi_v2
    assert doi_v2["identifier"]
    assert doi_v2["provider"] == "datacite"
    assert doi_v2["client"] == "datacite"  # Default since no values given
    assert doi_v1 != doi_v2

    doi_v2_pid = doi_provider.get(doi_v2["identifier"])
    assert doi_v2_pid.object_uuid == record_v2.id

    assert doi_v1 != doi_v2
