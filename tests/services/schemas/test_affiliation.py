# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test affiliations schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import AffiliationSchema


def test_valid_id():
    valid_id = {
        "id": "test",
    }
    assert valid_id == AffiliationSchema().load(valid_id)


def test_valid_name():
    valid_name = {
        "name": "Entity One"
    }
    assert valid_name == AffiliationSchema().load(valid_name)


def test_valid_both_id_name():
    valid_id_name = {
        "id": "test",
        "name": "Entity One"
    }
    assert valid_id_name == AffiliationSchema().load(valid_id_name)


def test_invalid_empty():
    invalid_empty = {}
    with pytest.raises(ValidationError):
        data = AffiliationSchema().load(invalid_empty)
