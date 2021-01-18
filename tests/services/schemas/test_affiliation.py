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
        "identifiers": [{
            "identifier": "03yrm5c26",
            "scheme": "ror"
        }]
    }
    assert valid_full == AffiliationSchema().load(valid_full)


def test_valid_no_identifiers():
    valid_affiliation = {
        "name": "Entity One",
    }
    assert valid_affiliation == AffiliationSchema().load(valid_affiliation)


def test_valid_empty_identifiers():
    valid_affiliation = {
        "name": "Entity One",
        "identifiers": []
    }
    assert valid_affiliation == AffiliationSchema().load(valid_affiliation)


def test_valid_empty_scheme():
    valid_affiliation = {
        "name": "Entity One",
        "identifiers": [{
            "identifier": "03yrm5c26",
            "scheme": ""
        }]
    }

    loaded = AffiliationSchema().load(valid_affiliation)
    valid_affiliation["identifiers"][0]["scheme"] = "ror"
    assert valid_affiliation == loaded


def test_invalid_no_name():
    invalid_no_name = {
        "identifiers": [{
            "identifier": "03yrm5c26",
            "scheme": "ror"
        }]
    }
    with pytest.raises(ValidationError):
        data = AffiliationSchema().load(invalid_no_name)


def test_invalid_empty_identifier():
    invalid_value = {
        "name": "Entity One",
        "identifiers": [{
            "scheme": "ror"
        }]
    }
    with pytest.raises(ValidationError):
        data = AffiliationSchema().load(invalid_value)


def test_invalid_value():
    invalid_no_value = {
        "name": "Entity One",
        "identifiers": [{
            "identifier": "inv",
            "scheme": "ror"
        }]
    }

    with pytest.raises(ValidationError):
        data = AffiliationSchema().load(invalid_no_value)


def test_invalid_unkown():
    invalid_unknown = {
        "name": "Entity One",
        "identifiers": [{
            "identifier": "12345abcde",
            "scheme": "unknown"
        }]
    }

    with pytest.raises(ValidationError):
        data = AffiliationSchema().load(invalid_unknown)


def test_invalid_empty():
    invalid_empty = {
        "name": "Entity One",
        "identifiers": [{}]
    }

    with pytest.raises(ValidationError):
        data = AffiliationSchema().load(invalid_empty)
