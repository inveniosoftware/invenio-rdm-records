# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for the service ExternalPIDsComponent."""

from functools import partial

import pytest
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PIDStatus
from marshmallow import ValidationError

from invenio_rdm_records.services import RDMRecordService
from invenio_rdm_records.services.components import ExternalPIDsComponent
from invenio_rdm_records.services.config import RDMRecordServiceConfig
from invenio_rdm_records.services.pids.providers import BaseClient, \
    BasePIDProvider, UnmanagedPIDProvider


class TestRecord:
    """Custom record to ease component testing."""

    pids = None

    def get(self, attr, default):
        """Dummy accesor to pids, emulates descriptor."""
        return self.pids


class TestClient(BaseClient):
    """Dummy PID Client class."""

    def __init__(self, **kwards):
        """Constructor."""
        pass


class TestBaseProvider(BasePIDProvider):
    """Test provider."""

    def __init__(self, name="testprov", pid_type="testid", **kwargs):
        """Constructor."""
        self.counter = 1
        super(TestBaseProvider, self).__init__(
            name=name, pid_type=pid_type, **kwargs)

    def _generate_id(self, **kwargs):
        """Generates an identifier value."""
        self.counter += 1
        return self.counter - 1


class TestServiceConfig(RDMRecordServiceConfig):
    """Custom service config with only pid providers."""
    pids_providers = {
        "test": TestBaseProvider,
        "unmanaged": UnmanagedPIDProvider
    }

    providers_clients = {
        "test-client": TestClient
    }


class TestService(RDMRecordService):
    """Custom service."""

    def __init__(self, config, **kwargs):
        """Constructor for RDMRecordService."""
        super(TestService, self).__init__(config, **kwargs)


@pytest.fixture(scope="function")
def unmanaged_pids_cmp():
    service = TestService(config=TestServiceConfig())

    return ExternalPIDsComponent(service=service)


#
# External Provider
#

def test_create_valid_pid_unmanaged(unmanaged_pids_cmp):
    data = {"pids": {
        "unmanaged": {
            "identifier": "somevalue",
            "provider": "unmanaged",
        }
    }}

    record = TestRecord()
    unmanaged_pids_cmp.create(identity=None, data=data, record=record)

    assert record.pids["unmanaged"]["identifier"] == "somevalue"
    assert record.pids["unmanaged"]["provider"] == "unmanaged"


def test_create_unmanaged_pid_no_value(unmanaged_pids_cmp):
    data = {"pids": {
        "unmanaged": {
            "provider": "unmanaged",
        }
    }}

    record = TestRecord()
    unmanaged_pids_cmp.create(identity=None, data=data, record=record)

    assert not record.pids["unmanaged"].get("identifier")
    assert record.pids["unmanaged"]["provider"] == "unmanaged"


def test_publish_valid_pid_unmanaged(unmanaged_pids_cmp):
    data = {"pids": {
        "unmanaged": {
            "identifier": "somevalue",
            "provider": "unmanaged",
        }
    }}

    record = TestRecord()
    draft = TestRecord()
    unmanaged_pids_cmp.create(identity=None, data=data, record=draft)
    unmanaged_pids_cmp.publish(
        identity=None, data=data, draft=draft, record=record)

    assert record.pids["unmanaged"]["identifier"] == "somevalue"
    assert record.pids["unmanaged"]["provider"] == "unmanaged"


def test_publish_unmanaged_pid_no_value(unmanaged_pids_cmp):
    data = {"pids": {
        "unmanaged": {
            "provider": "unmanaged",
        }
    }}

    record = TestRecord()
    draft = TestRecord()
    unmanaged_pids_cmp.create(identity=None, data=data, record=draft)
    # NOTE: Cannot publish without identifier value because the system
    # cannot assign one (is unmanaged)
    with pytest.raises(ValidationError):
        unmanaged_pids_cmp.publish(
            identity=None, data=data, draft=draft, record=record)


#
# Base/General provider
#

def test_create_invalid_provider_name(app, external_pids_cmp):
      # PIDS-FIXME: Will be correct when #514 fixed
      data = {"pids": {
          "test": {
              "provider": "invalid",
              "client": "test-client"
          }
      }}

      with pytest.raises(ValidationError):
          external_pids_cmp.create(
              identity=None, data=data, record=TestRecord())


def test_update_no_change_pid(app, unmanaged_pids_cmp):
    data = {"pids": {
        "test": {
            "identifier": "1234",
            "provider": "testprov",
            "client": "test-client"
        }
    }}

    record = TestRecord()
    unmanaged_pids_cmp.create(identity=None, data=data, record=record)
    unmanaged_pids_cmp.update_draft(identity=None, data=data, record=record)

    assert record.pids["test"]["identifier"] == "1234"
    assert record.pids["test"]["provider"] == "testprov"
    assert record.pids["test"]["client"] == "test-client"


def test_update_add_pid_no_identifier(app, unmanaged_pids_cmp):
    data = {"pids": {}}
    record = TestRecord()
    unmanaged_pids_cmp.create(identity=None, data=data, record=record)

    data["pids"] = {
        "test": {
            "provider": "testprov",
            "client": "test-client"
        }
    }
    unmanaged_pids_cmp.update_draft(identity=None, data=data, record=record)

    assert not record.pids["test"].get("identifier")
    assert record.pids["test"]["provider"] == "testprov"
    assert record.pids["test"]["client"] == "test-client"


def test_update_add_pid_with_identifier(app, unmanaged_pids_cmp):
    data = {"pids": {}}
    record = TestRecord()
    unmanaged_pids_cmp.create(identity=None, data=data, record=record)

    data["pids"] = {
        "test": {
            "identifier": "1234",
            "provider": "testprov",
            "client": "test-client"
        }
    }
    unmanaged_pids_cmp.update_draft(identity=None, data=data, record=record)

    assert record.pids["test"]["identifier"] == "1234"
    assert record.pids["test"]["provider"] == "testprov"
    assert record.pids["test"]["client"] == "test-client"


def test_update_add_reserved_pid(app, unmanaged_pids_cmp):
     # PIDS-FIXME: implement
     assert True == False


def test_publish_without_pid_value(app, unmanaged_pids_cmp):
    data = {"pids": {
        "test": {
            "provider": "testprov",
            "client": "test-client"
        }
    }}

    record = TestRecord()
    draft = TestRecord()
    unmanaged_pids_cmp.create(identity=None, data=data, record=draft)
    unmanaged_pids_cmp.publish(
        identity=None, data=data, draft=draft, record=record)

    assert record.pids["test"]["identifier"]  # value depends on the counter


def test_publish_with_pid_value(app, external_pids_cmp):
      data = {"pids": {
          "test": {
              "identifier": "1234",
              "provider": "testprov",
              "client": "test-client"
          }
      }}

      record = TestRecord()
      draft = TestRecord()
      external_pids_cmp.create(identity=None, data=data, record=draft)
      external_pids_cmp.publish(
              identity=None, data=data, draft=draft, record=record)

      assert record.pids["test"]["identifier"] == "1234"
      assert record.pids["test"]["provider"] == "testprov"
      assert record.pids["test"]["client"] == "test-client"


def test_publish_with_pid_value_not_created(app, unmanaged_pids_cmp):
    data = {"pids": {
        "test": {
            "identifier": "somevalue",
            "provider": "testprov",
            "client": "test-client"
        }
    }}

    record = TestRecord()
    draft = TestRecord()
    unmanaged_pids_cmp.create(identity=None, data=data, record=draft)
    with pytest.raises(PIDDoesNotExistError):
        unmanaged_pids_cmp.publish(
            identity=None, data=data, draft=draft, record=record)
