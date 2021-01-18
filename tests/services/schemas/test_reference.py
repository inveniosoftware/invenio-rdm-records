# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test rights schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import MetadataSchema, \
    ReferenceSchema


def test_valid_reference():
    """Test references schema."""
    valid_full = {
        "reference": "Reference to something et al.",
        "identifier": "0000 0001 1456 7559",
        "scheme": "isni"
    }
    assert valid_full == ReferenceSchema().load(valid_full)


def test_valid_minimal_reference():
    valid_minimal = {
        "reference": "Reference to something et al."
    }
    assert valid_minimal == ReferenceSchema().load(valid_minimal)


def test_invalid_no_reference():
    invalid_no_reference = {
        "identifier": "0000 0001 1456 7559",
        "scheme": "isni"
    }
    with pytest.raises(ValidationError):
        data = ReferenceSchema().load(invalid_no_reference)


def test_invalid_scheme_reference():
    invalid_scheme = {
        "reference": "Reference to something et al.",
        "identifier": "0000 0001 1456 7559",
        "scheme": "Invalid"
    }
    with pytest.raises(ValidationError):
        data = ReferenceSchema().load(invalid_scheme)


def test_invalid_extra_right():
    invalid_extra = {
        "reference": "Reference to something et al.",
        "identifier": "0000 0001 1456 7559",
        "scheme": "Invalid",
        "extra": "field"
    }
    with pytest.raises(ValidationError):
        data = ReferenceSchema().load(invalid_extra)


@pytest.mark.parametrize("references", [
    ([]),
    ([{
        "reference": "Reference to something et al.",
        "identifier": "0000 0001 1456 7559",
        "scheme": "isni"
    }, {
        "reference": "Reference to something et al."
    }])
])
def test_valid_rights(references, minimal_record, vocabulary_clear):
    metadata = minimal_record['metadata']
    # NOTE: this is done to get possible load transformations out of the way
    metadata = MetadataSchema().load(metadata)
    metadata['references'] = references

    assert metadata == MetadataSchema().load(metadata)
