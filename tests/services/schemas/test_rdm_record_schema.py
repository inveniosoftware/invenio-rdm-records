# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test pids schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas import RDMRecordSchema


@pytest.mark.skip("PIDS-FIXME re-enable")
def test_valid_pid(app, db, minimal_record, location):
    valid_full = {
        "doi": {
            "identifier": "10.5281/zenodo.1234",
            "provider": "datacite",
            "client": "zenodo"
        }
    }

    minimal_record["pids"] = valid_full
    assert valid_full == RDMRecordSchema().load(minimal_record)["pids"]


@pytest.mark.skip("PIDS-FIXME re-enable")
def test_valid_external(app, db, minimal_record, location):
    valid_full = {
        "doi": {
            "identifier": "10.5281/zenodo.1234",
            "provider": "external",
        }
    }

    minimal_record["pids"] = valid_full
    assert valid_full == RDMRecordSchema().load(minimal_record)["pids"]


@pytest.mark.skip("PIDS-FIXME re-enable")
def test_valid_unknown_scheme(app, db, minimal_record, location):
    valid_full = {
        "rand-unknown": {
            "identifier": "aa::bb::11:::22",
            "provider": "datacite",
            "client": "zenodo"
        }
    }

    minimal_record["pids"] = valid_full
    assert valid_full == RDMRecordSchema().load(minimal_record)["pids"]


@pytest.mark.skip("PIDS-FIXME re-enable")
def test_invalid_pid(app, db, minimal_record, location):
    invalid_pid_type = {
        "doi": {
            "identifier": "10.5281/zenodo.1234",
            "provider": "datacite",
            "client": "zenodo"
        },
        "invalid": {
            "identifier": "10.5281/zenodo.1234",
            "provider": "datacite",
            "client": "zenodo"
        }
    }

    minimal_record["pids"] = invalid_pid_type
    with pytest.raises(ValidationError):
        data = RDMRecordSchema().load(minimal_record)


@pytest.mark.skip("PIDS-FIXME re-enable")
def test_invalid_external_with_client(app, db, minimal_record, location):
    invalid_pid_type = {
        "doi": {
            "identifier": "10.5281/zenodo.1234",
            "provider": "external",
            "client": "zenodo"
        }
    }

    minimal_record["pids"] = invalid_pid_type
    with pytest.raises(ValidationError):
        data = RDMRecordSchema().load(minimal_record)
