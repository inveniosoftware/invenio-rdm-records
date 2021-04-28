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


def test_valid_pid(app, db, minimal_record, location):
    # NOTE: PID attributes validity is checked at component level
    # At marshmallow level only the identifier's format is checked
    # based on the scheme value
    valid_full = {
        "doi": {
            "identifier": "10.5281/zenodo.1234",
            "provider": "datacite",
            "client": "zenodo"
        }
    }

    minimal_record["pids"] = valid_full
    assert valid_full == RDMRecordSchema().load(minimal_record)["pids"]


def test_valid_unmanaged(app, db, minimal_record, location):
    valid_full = {
        "doi": {
            "identifier": "10.5281/zenodo.1234",
            "provider": "unmanaged",
        }
    }

    minimal_record["pids"] = valid_full
    assert valid_full == RDMRecordSchema().load(minimal_record)["pids"]
