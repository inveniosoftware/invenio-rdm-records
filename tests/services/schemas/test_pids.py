# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-License-Identifier: MIT

"""Test pids schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.pids import PIDSchema


def test_valid_pid():
    """Test pids schema."""
    valid_full = {
        "identifier": "10.1234/zenodo.1234",
        "provider": "datacite",
        "client": "zenodo",
    }
    assert valid_full == PIDSchema().load(valid_full)


def test_valid_minimal_pid():
    valid_minimal = {"identifier": "oai:zenodo.org:12345", "provider": "zenodo"}
    assert valid_minimal == PIDSchema().load(valid_minimal)


def test_invalid_no_identifier():
    invalid_no_identifier = {"provider": "datacite", "client": "zenodo"}
    with pytest.raises(ValidationError):
        data = PIDSchema().load(invalid_no_identifier)


def test_invalid_no_provider():
    invalid_no_provider = {"identifier": "10.1234/zenodo.1234", "client": "zenodo"}
    with pytest.raises(ValidationError):
        data = PIDSchema().load(invalid_no_provider)


def test_invalid_extra_field():
    invalid_extra = {
        "identifier": "10.1234/zenodo.1234",
        "provider": "datacite",
        "client": "zenodo",
        "extra": "field",
    }
    with pytest.raises(ValidationError):
        data = PIDSchema().load(invalid_extra)
