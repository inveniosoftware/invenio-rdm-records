# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the service ExternalPIDsComponent."""

import pytest
from invenio_pidstore.models import PIDStatus
from marshmallow import ValidationError

from invenio_rdm_records.services.components import ExternalPIDsComponent
from invenio_rdm_records.services.pids.providers import BaseProvider, \
    ExternalProvider


class TestRecord:
    """Custom record to ease component testing."""
    pids = None


class TestPID:
    """Test PID mock class."""

    def __init__(self, identifier=None):
        """Constructor."""
        self.value = identifier or "1234"
        self.status = PIDStatus.RESERVED


class TestProvider(BaseProvider):
    """Custom provider for testing purposes."""

    def __init__(self, **kwargs):
        """Constructor."""
        super(TestProvider, self).__init__(name="test-invenio")

    def create(self, **kwargs):
        """Create a new PID."""
        return TestPID()

    # PIDS-FIXME: This should interact with the resolver?
    def get(self, pid_value, **kwargs):
        """Create a new PID."""
        return TestPID(pid_value)

    def validate(self, pid_attrs=None, **kwargs):
        """Validate the PID."""
        # PIDS-FIXME: Should this be moved to the base provider?
        given_provider = pid_attrs.get("provider")

        if self.name != given_provider:
            raise ValidationError(
                f"PID Provider {given_provider} not supported.",
                field_name="pids"
            )
        if pid_attrs.get("identifier") == "12345":
            raise ValidationError(
                "PID does not correspond to record.",
                field_name="pids"
            )


class TestService:
    """Custom service."""

    class TestServiceConfig:
        """Custom service config with only pid providers."""
        pids_providers = {
            "test": TestProvider(
                name="test-invenio",
                client="test_pid"
            ),
            # NOTE: Always require an external provider
            "external": ExternalProvider(name="test-external")
        }

    config = TestServiceConfig()


@pytest.fixture(scope="function")
def external_pids_cmp():
    return ExternalPIDsComponent(service=TestService())


def test_create_invalid_provider_name(external_pids_cmp):
    # Test that it fails on the provider validation step
    data = {"pids": {
        "test": {
            "provider": "test-invalid",
            "client": "test_pid"
        }
    }}

    with pytest.raises(ValidationError):
        external_pids_cmp.create(
            identity=None, data=data, record=TestRecord())


def test_create_valid_external_pid(external_pids_cmp):
    data = {"pids": {
        "external": {
            "identifier": "somevalue",
            "provider": "test-external",
        }
    }}

    record = TestRecord()
    external_pids_cmp.create(identity=None, data=data, record=record)

    assert record.pids["external"]["identifier"] == "somevalue"
    assert record.pids["external"]["provider"] == "test-external"


def test_create_external_pid_no_value(external_pids_cmp):
    data = {"pids": {
        "test": {
            "provider": "external",
        }
    }}

    with pytest.raises(ValidationError):
        external_pids_cmp.create(
            identity=None, data=data, record=TestRecord())


def test_update_no_change_pid(external_pids_cmp):
    data = {"pids": {
        "test": {
            "identifier": "1234",
            "provider": "test-invenio",
            "client": "test_pid"
        }
    }}

    record = TestRecord()
    external_pids_cmp.create(identity=None, data=data, record=record)
    external_pids_cmp.update_draft(identity=None, data=data, record=record)

    assert record.pids["test"]["identifier"] == "1234"
    assert record.pids["test"]["provider"] == "test-invenio"
    assert record.pids["test"]["client"] == "test_pid"


def test_update_add_pid_no_identifier(external_pids_cmp):
    data = {"pids": {}}
    record = TestRecord()
    external_pids_cmp.create(identity=None, data=data, record=record)

    data["pids"] = {"test": {
        "provider": "test-invenio",
        "client": "test_pid"
    }}
    external_pids_cmp.update_draft(identity=None, data=data, record=record)

    assert not record.pids["test"].get("identifier")
    assert record.pids["test"]["provider"] == "test-invenio"
    assert record.pids["test"]["client"] == "test_pid"


def test_update_add_pid_no_identifier(external_pids_cmp):
    data = {"pids": {}}
    record = TestRecord()
    external_pids_cmp.create(identity=None, data=data, record=record)

    data["pids"] = {"test": {
        "identifier": "1234",
        "provider": "test-invenio",
        "client": "test_pid"
    }}
    external_pids_cmp.update_draft(identity=None, data=data, record=record)

    assert record.pids["test"]["identifier"] == "1234"
    assert record.pids["test"]["provider"] == "test-invenio"
    assert record.pids["test"]["client"] == "test_pid"


def test_update_add_reserved_pid(external_pids_cmp):
    data = {"pids": {}}
    record = TestRecord()
    external_pids_cmp.create(identity=None, data=data, record=record)

    data["pids"] = {"test": {
        "identifier": "12345",
        "provider": "test-invenio",
        "client": "test_pid"
    }}

    with pytest.raises(ValidationError):
        external_pids_cmp.update_draft(
            identity=None, data=data, record=TestRecord())


@pytest.mark.skip("PIDS-FIXME re-enable")
def test_publish_without_pid_value(external_pids_cmp):
    data = {"pids": {
        "test": {
            "provider": "test-invenio",
            "client": "test_pid"
        }
    }}

    record = TestRecord()
    external_pids_cmp.publish(identity=None, data=data, record=record)

    assert record.pids["test"]["identifier"] == "1234"


@pytest.mark.skip("PIDS-FIXME re-enable")
def test_publish_with_pid_value(external_pids_cmp):
    data = {"pids": {
        "test": {
            "identifier": "somevalue",
            "provider": "test-invenio",
            "client": "test_pid"
        }
    }}

    with pytest.raises(ValidationError):
        external_pids_cmp.publish(
            identity=None, data=data, record=TestRecord())
