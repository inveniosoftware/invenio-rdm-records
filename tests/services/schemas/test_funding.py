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
    "title": {"en": "Some award"},
    "number": "100",
    "identifiers": [
        {"scheme": "url", "identifier": "https://example.com"}
    ],
}

FUNDER = {
    "id": "00k4n6c32",
}


def test_valid_funder_funding(app):
    valid_funding = {
        "funder": FUNDER
    }
    assert valid_funding == FundingSchema().load(valid_funding)


def test_valid_award_funder_funding(app):
    valid_funding = {
        "funder": FUNDER,
        "award": AWARD
    }
    assert valid_funding == FundingSchema().load(valid_funding)


def test_valid_award_id(app):
    valid_funding = {
        "funder": FUNDER,
        "award": {"id": "00k4n6c32::100"}
    }
    assert valid_funding == FundingSchema().load(valid_funding)


def test_invalid_empty_funding(app):
    invalid_funding = {
        "award": AWARD,
    }
    with pytest.raises(ValidationError):
        data = FundingSchema().load(invalid_funding)


@pytest.mark.parametrize("funding", [
    ([]),
    ([{"funder": FUNDER}, {"funder": FUNDER, "award": AWARD}])
])
def test_valid_funding(funding, minimal_record):
    metadata = minimal_record['metadata']
    # NOTE: this is done to get possible load transformations out of the way
    metadata = MetadataSchema().load(metadata)
    metadata['funding'] = funding

    assert metadata == MetadataSchema().load(metadata)
