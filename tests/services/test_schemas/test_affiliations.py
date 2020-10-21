# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test affiliations schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import AffiliationSchema


def test_valid():
    valid_full = {
        "name": "Entity One",
        "identifiers": {
            "ror": "03yrm5c26"
        }
    }
    assert valid_full == AffiliationSchema().load(valid_full)


def test_invalid_no_name():
    invalid_no_name = {
        "identifiers": {
            "ror": "03yrm5c26"
        }
    }
    with pytest.raises(ValidationError):
        data = AffiliationSchema().load(invalid_no_name)


def test_invalid_empty_value():
    invalid_value = {
        "name": "Entity One",
        "identifiers": {
            "ror": ""
        }
    }
    with pytest.raises(ValidationError):
        data = AffiliationSchema().load(invalid_value)


def test_invalid_empty_key():
    invalid_key = {
        "name": "Entity One",
        "identifiers": {
            "": "03yrm5c26"
        }
    }
    with pytest.raises(ValidationError):
        data = AffiliationSchema().load(invalid_key)


def test_invalid_value():
    invalid_no_value = {
        "name": "Entity One",
        "identifiers": {
            "ror": "inv"
        }
    }
    with pytest.raises(ValidationError):
        data = AffiliationSchema().load(invalid_no_value)


def test_valid_unkown():
    valid_unknown = {
        "name": "Entity One",
        "identifiers": {
            "unknown": "12345abcde"
        }
    }
    assert valid_unknown == AffiliationSchema().load(valid_unknown)
