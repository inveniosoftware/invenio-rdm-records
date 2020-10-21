# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test identifier schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import IdentifierSchema, \
    MetadataSchema


def test_valid_identifier():
    valid = {
        "identifier": "10.5281/zenodo.9999999",
        "scheme": "doi"
    }
    assert valid == IdentifierSchema().load(valid)


def test_invalid_no_identifier():
    invalid = {
        "scheme": "doi"
    }
    with pytest.raises(ValidationError):
        data = IdentifierSchema().load(invalid)


def test_invalid_no_schema():
    invalid = {
        "identifier": "10.5281/zenodo.9999999",
    }
    with pytest.raises(ValidationError):
        data = IdentifierSchema().load(invalid)


def test_valid_empty_list(app, minimal_record):
    metadata = minimal_record['metadata']
    metadata['identifiers'] = []
    data = MetadataSchema().load(metadata)
    assert data['identifiers'] == metadata['identifiers']


def test_valid_multiple_identifiers(app, minimal_record):
    metadata = minimal_record['metadata']
    metadata['identifiers'] = [
        {"identifier": "10.5281/zenodo.9999999", "scheme": "doi"},
        {"identifier": "ark:/123/456", "scheme": "ark"}
    ]
    data = MetadataSchema().load(metadata)
    assert data['identifiers'] == metadata['identifiers']


def test_valid_duplicate_type(app, minimal_record):
    # NOTE: Duplicates are accepted, there is no de-duplication
    metadata = minimal_record['metadata']
    metadata['identifiers'] = [
        {"identifier": "10.5281/zenodo.9999999", "scheme": "doi"},
        {"identifier": "10.5281/zenodo.0000000", "scheme": "doi"}
    ]
    data = MetadataSchema().load(metadata)
    assert data['identifiers'] == metadata['identifiers']
