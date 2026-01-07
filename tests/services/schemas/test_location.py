# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test location schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import LocationSchema, MetadataSchema


@pytest.fixture(scope="function")
def valid_full_location():
    """Input data (as coming from the view layer)."""
    return {
        "geometry": {"type": "Point", "coordinates": [-32.94682, -60.63932]},
        "place": "test location place",
        "description": "test location description",
        "identifiers": [
            {"identifier": "Q39", "scheme": "wikidata"},
            {"identifier": "https://www.geonames.org/2660646", "scheme": "geonames"},
        ],
    }


def test_valid_full(app, valid_full_location):
    assert valid_full_location == LocationSchema().load(valid_full_location)


@pytest.mark.parametrize(
    "valid_minimal_location",
    [
        ({"geometry": {"type": "Point", "coordinates": [-32.94682, -60.63932]}}),
        ({"description": "test location description"}),
        ({"place": "test location place"}),
        ({"identifiers": [{"identifier": "Q39", "scheme": "wikidata"}]}),
    ],
)
def test_valid_minimal(app, valid_minimal_location):
    assert valid_minimal_location == LocationSchema().load(valid_minimal_location)


def test_invalid_geometry_type(app, valid_full_location):
    valid_full_location["geometry"]["type"] = "invalid"

    with pytest.raises(ValidationError):
        data = LocationSchema().load(valid_full_location)


def test_invalid_wrong_geometry_type(app, valid_full_location):
    # type multipoint, but point coordinates
    valid_full_location["geometry"]["type"] = "MultiPoint"

    with pytest.raises(ValidationError):
        data = LocationSchema().load(valid_full_location)


def test_invalid_empty(app, valid_full_location):
    with pytest.raises(ValidationError):
        data = LocationSchema().load({})


def test_valid_single_location(app, minimal_record, valid_full_location):
    metadata = minimal_record["metadata"]
    # NOTE: this is done to get possible load transformations out of the way
    metadata = MetadataSchema().load(metadata)
    metadata["locations"] = {"features": [valid_full_location]}

    assert metadata == MetadataSchema().load(metadata)


def test_valid_multiple_locations(app, minimal_record, valid_full_location):
    metadata = minimal_record["metadata"]
    # NOTE: this is done to get possible load transformations out of the way
    metadata = MetadataSchema().load(metadata)
    metadata["locations"] = {"features": [valid_full_location, valid_full_location]}

    assert metadata == MetadataSchema().load(metadata)


def test_invalid_no_list_location(app, minimal_record, valid_full_location):
    metadata = minimal_record["metadata"]
    metadata["locations"] = {"features": valid_full_location}

    with pytest.raises(ValidationError):
        data = MetadataSchema().load(metadata)
