# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test award schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import AwardSchema


def test_valid_full():
    valid_full = {
        "title": "Some award",
        "number": "100",
        "identifier": "10.5281/zenodo.9999999",
        "scheme": "doi"
    }
    assert valid_full == AwardSchema().load(valid_full)


def test_valid_minimal():
    valid_minimal = {
        "title": "Some award",
        "number": "100",
    }
    assert valid_minimal == AwardSchema().load(valid_minimal)


def test_invalid_no_title():
    invalid_no_title = {
        "number": "100",
        "identifier": "10.5281/zenodo.9999999",
        "scheme": "doi"
    }
    with pytest.raises(ValidationError):
        data = AwardSchema().load(invalid_no_title)


def test_invalid_no_number():
    invalid_no_number = {
        "title": "Some award",
        "identifier": "10.5281/zenodo.9999999",
        "scheme": "doi"
    }
    with pytest.raises(ValidationError):
        data = AwardSchema().load(invalid_no_number)
