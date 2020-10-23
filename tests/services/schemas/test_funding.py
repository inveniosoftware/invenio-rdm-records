# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test funding schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import FundingSchema, \
    MetadataSchema

AWARD = {
    "title": "Some award",
    "number": "100",
    "identifier": "10.5281/zenodo.9999999",
    "scheme": "doi"
}

FUNDER = {
    "name": "Someone",
    "identifier": "10.5281/zenodo.9999999",
    "scheme": "doi"
}


def test_valid_award_funding():
    valid_funding = {
        "award": AWARD
    }
    assert valid_funding == FundingSchema().load(valid_funding)


def test_valid_funder_funding():
    valid_funding = {
        "funder": FUNDER
    }
    assert valid_funding == FundingSchema().load(valid_funding)


def test_valid_award_funder_funding():
    valid_funding = {
        "funder": FUNDER,
        "award": AWARD
    }
    assert valid_funding == FundingSchema().load(valid_funding)


def test_invalid_empty_funding():
    invalid_funding = {}
    with pytest.raises(ValidationError):
        data = FundingSchema().load(invalid_funding)


@pytest.mark.parametrize("funding", [
    ([]),
    ([{"funder": FUNDER}, {"award": AWARD}])
])
def test_valid_rights(funding, minimal_record, vocabulary_clear):
    metadata = minimal_record['metadata']
    metadata['funding'] = funding

    assert metadata == MetadataSchema().load(metadata)
