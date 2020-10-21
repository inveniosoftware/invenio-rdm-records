# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test date schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import DateSchema


def test_valid_full_date():
    valid_full = {
        "date": "2020-12-31",
        "description": "Random test date",
        "type": "other"
    }
    assert valid_full == DateSchema().load(valid_full)


def test_minimal_date():
    # Note that none start or end are required. But it validates that at
    # least one of them is present.
    valid_minimal = {
        "date": "2020-12-31",
        "type": "other"
    }
    assert valid_minimal == DateSchema().load(valid_minimal)


def test_valid_range():
    valid_range = {
        "date": "2020-01/2020-12",
        "type": "other"
    }
    assert valid_range == DateSchema().load(valid_range)


def test_invalid_no_type():
    invalid_no_type = {
        "date": "2020-12-31",
        "description": "Random test date",
    }
    with pytest.raises(ValidationError):
        data = DateSchema().load(invalid_no_type)


def test_invalid_no_date():
    invalid_no_date = {
        "description": "Random test date",
        "type": "other"
    }
    with pytest.raises(ValidationError):
        data = DateSchema().load(invalid_no_date)


def test_invalid_range():
    invalid_range = {
        "date": "2021-01/2020-12",
        "description": "Random test date",
    }
    with pytest.raises(ValidationError):
        data = DateSchema().load(invalid_range)
