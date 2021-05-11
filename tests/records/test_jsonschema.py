# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""JSONSchema tests."""

import json
import unittest.mock
from os.path import dirname, join

import pytest
from jsonschema.exceptions import ValidationError

from invenio_rdm_records.records.api import RDMRecord as Record


#
# Assertion helpers
#
def validates(data):
    """Assertion function used to validate according to the schema."""
    data["$schema"] = "local://records/record-v3.0.0.json"
    Record(data).validate()
    return True


def validates_meta(data):
    """Validate metadata fields."""
    return validates({"metadata": data})


def fails(data):
    """Assert that validation fails."""
    pytest.raises(ValidationError, validates, data)
    return True


def fails_meta(data):
    """Assert that validation fails for metadata."""
    pytest.raises(ValidationError, validates_meta, data)
    return True


#
# Fixtures
#
@pytest.fixture()
def person():
    """Person for creator or contributor."""
    return {
        "person_or_org": {
            "name": "Nielsen, Lars Holm",
            "type": "personal",
            "given_name": "Lars Holm",
            "family_name": "Nielsen",
            "identifiers": [{
                "scheme": "orcid",
                "identifier": "0000-0001-8135-3489"
            }],
        },
        "affiliations": [{
            "name": "CERN",
            "identifiers": [{
                "scheme": "ror",
                "identifier": "01ggx4157"
            }, {
                "scheme": "isni",
                "identifier": "000000012156142X"
            }]
        }]
    }


@pytest.fixture()
def org():
    """Organization for creator or contributor."""
    return {
        "person_or_org": {
            "name": "CERN",
            "type": "organizational",
            "identifiers": [{
                "scheme": "ror",
                "identifier": "01ggx4157"
            }],
        },
        "affiliations": [{
            "name": "CERN",
            "identifiers": [{
                "scheme": "ror",
                "identifier": "..."
            }],
        }]
    }


def _load_json(filename):
    with open(join(dirname(__file__), filename), 'rb') as fp:
        return json.load(fp)


#
# Test a full record
#
def test_full_record(appctx):
    """Test validation of a full record example."""
    assert validates(_load_json('full-record.json'))


def test_tombstone_record(appctx):
    """Test validation of a tombstone record example."""
    assert validates(_load_json('tombstone.json'))


#
# Tests internal/external identifiers
#
def test_id(appctx):
    """Test id."""
    assert validates({"id": "12345-abcd"})
    assert fails({"id": 1})


def test_pids(appctx):
    """Test external pids."""
    assert validates({"pids": {
        "doi": {
            "identifier": "10.12345", "provider": "datacite", "client": "test"
        }
    }})
    assert validates({"pids": {
        "doi": {
            "identifier": "10.12345", "provider": "datacite", "client": "test"
        },
        "oai": {"identifier": "oai:10.12345", "provider": "local"},
    }})
    # Extra property
    assert fails({"pids": {
        "oai": {
            "identifier": "oai:10.12345",
            "provider": "local",
            "invalid": "test"
        }
    }})
    # Not a string
    assert fails({"pids": {
        "oai": {"identifier": 1, "provider": "local"}
    }})


#
# Tests metadata
#
def test_metadata(appctx):
    """Test empty metadata."""
    assert validates({"metadata": {}})


def test_resource_type(appctx):
    """Test resource type."""
    assert fails_meta({"resource_type": {}})
    assert validates_meta({"resource_type": {"type": "publication"}})
    assert validates_meta(
        {"resource_type": {"type": "publication", "subtype": "test"}})
    assert fails_meta(
        {"resource_type": {"type": "publication", "invalid": "test"}})


def test_creators(appctx, person, org):
    """Test creators."""
    assert fails_meta({"creators": {}})
    assert validates_meta({"creators": []})
    assert validates_meta({"creators": [{"person_or_org": {
        "name": "test", "type": "organizational"}}]})

    assert validates_meta({"creators": [person]})
    assert validates_meta({"creators": [org]})
    assert validates_meta({"creators": [person, org]})

    # Additional prop fails
    assert fails_meta({"creators": [{
        "person_or_org": {
            "name": "test",
            "type": "organizational"
        },
        "invalid": "test"
    }]})
    person["affiliations"][0]["invalid"] = "test"
    assert fails_meta({"creators": [person]})


def test_title(appctx):
    """Test title property."""
    assert validates_meta({"title": "Test"})
    assert fails_meta({"title": {}})


def test_additional_titles(appctx):
    """Test additional titles property."""
    assert fails_meta({"additional_titles": "Test"})
    assert validates_meta({"additional_titles": []})
    assert validates_meta({"additional_titles": [
        {"title": "Test"}
    ]})
    assert validates_meta({"additional_titles": [
        {"title": "Test", "type": "subtitle", "lang": "dan"},
    ]})
    assert fails_meta({"additional_titles": [
        {"title": "Test", "invalid": "invalid"}
    ]})


def test_publisher(appctx):
    """Test publisher property."""
    assert validates_meta({"publisher": "Zenodo"})
    assert fails_meta({"publisher": 1})
    assert fails_meta({"publisher": {}})


def test_publication_date(appctx):
    """Test publisher property."""
    assert validates_meta({"publication_date": "2020-09-01"})
    assert validates_meta({"publication_date": "2020-09"})
    assert validates_meta({"publication_date": "2018/2020-09"})
    assert fails_meta({"publisher": 2020})


def test_subjects(appctx):
    """Test publisher property."""
    assert validates_meta({"subjects": []})
    sub_min = {"subject": "Computing"}
    sub_full = {"subject": "Computing", "scheme": "test", "identifier": "test"}
    sub_invalid = {"subject": "Test", "invalid": "test"}
    assert validates_meta({"subjects": [sub_min]})
    assert validates_meta({"subjects": [sub_full]})
    assert validates_meta({"subjects": [sub_min, sub_full]})
    assert fails_meta({"subjects": [sub_invalid]})


def test_contributors(appctx, person, org):
    """Test contributors."""
    assert fails_meta({"contributors": {}})
    assert validates_meta({"contributors": []})
    assert validates_meta({"contributors": [{
        "person_or_org": {"name": "test", "type": "organizational"},
        "role": "other"
    }]})

    person["role"] = "other"
    org["role"] = "hosting_institution"

    assert validates_meta({"contributors": [person]})
    assert validates_meta({"contributors": [org]})
    assert validates_meta({"contributors": [person, org]})

    # Additional prop fails
    assert fails_meta({"contributors": [
        {"person_or_org": {"name": "test"}, "invalid": "test"}]})
    person["affiliations"][0]["invalid"] = "test"
    assert fails_meta({"contributors": [person]})


def test_dates(appctx):
    """Test dates."""
    assert fails_meta({"dates": {}})
    assert validates_meta({"dates": []})
    assert validates_meta({"dates": [{"date": "test"}, ]})
    assert validates_meta({"dates": [
        {"date": "test", "type": "other", "description": "A date"}, ]})
    # Additional prop fails
    assert fails_meta({"dates": [{"date": "test", "invalid": "test"}, ]})


def test_languages(appctx):
    """Test language property."""
    assert validates_meta({"languages": [{"id": "dan"}, {"id": "eng"}]})
    assert fails_meta({"languages": ["da"]})
    assert fails_meta({"languages": "dan"})
    assert fails_meta({"languages": ["invalid"]})


def test_identifiers(appctx):
    """Test alternate identifiers property."""
    assert fails_meta({"identifiers": 1})
    assert validates_meta({"identifiers": []})
    assert validates_meta({"identifiers": [
        {"identifier": "10.1234/test", "scheme": "doi"}
    ]})
    # Additional property
    assert fails_meta({"identifiers": [
        {"identifier": "10.1234/test", "invalid": "doi"}
    ]})
    # Unique
    assert fails_meta({"identifiers": [
        {"identifier": "10.1234/test", "scheme": "doi"},
        {"identifier": "10.1234/test", "scheme": "doi"}
    ]})


def test_related_identifiers(appctx):
    """Test alternate identifiers property."""
    assert fails_meta({"related_identifiers": 1})
    assert validates_meta({"related_identifiers": []})
    assert validates_meta({"related_identifiers": [
        {"identifier": "10.1234/test", "scheme": "doi",
         "relation_type": "cites"}
    ]})
    assert validates_meta({"related_identifiers": [
        {"identifier": "10.1234/test", "relation_type": "cites"}
    ]})
    assert validates_meta({"related_identifiers": [
        {"identifier": "10.1234/test", "relation_type": "cites"}
    ]})
    # Additional property
    assert fails_meta({"related_identifiers": [
        {"identifier": "10.1234/test", "invalid": "doi"}
    ]})
    # Unique
    assert fails_meta({"related_identifiers": [
        {"identifier": "10.1234/test", "scheme": "doi",
         "relation_type": "cites"},
        {"identifier": "10.1234/test", "scheme": "doi",
         "relation_type": "cites"}
    ]})


def test_sizes(appctx):
    """Test sizes property."""
    assert validates_meta({"sizes": ["11 pages"]})
    assert fails_meta({"sizes": [1]})
    assert fails_meta({"sizes": "11 pages"})


def test_formats(appctx):
    """Test formats property."""
    assert validates_meta({"formats": ["application/pdf"]})
    assert fails_meta({"formats": [1]})
    assert fails_meta({"formats": "PDF"})


def test_version(appctx):
    """Test version property."""
    assert validates_meta({"version": "v1.0"})
    assert fails_meta({"version": 1})
    assert fails_meta({"version": {}})


def test_rights(appctx):
    """Test rights property."""
    assert fails_meta({"rights": 1})
    assert validates_meta({"rights": []})
    lic_full = {
        "title": "Creative Commons Attribution 4.0 International",
        "description": "A Description",
        "link": "https://creativecommons.org/licenses/by/4.0/"
    }
    lic_min = {
        "title": "Copyright (C) 2020. All rights reserved.",
    }
    lic_linked = {
        "id": "cc-by-4.0"
    }
    assert validates_meta({"rights": [lic_full]})
    assert validates_meta({"rights": [lic_min]})
    assert validates_meta({"rights": [lic_linked]})

    # Additional property
    lic_full["invalid"] = "test"
    assert fails_meta({"rights": [lic_full]})
    # Not a URI
    lic_min["url"] = "invalid"
    assert fails_meta({"rights": [lic_full]})


def test_description(appctx):
    """Test description property."""
    assert validates_meta({"description": "Bla bla bla"})
    assert fails_meta({"description": 1})
    assert fails_meta({"description": {}})


def test_additional_descriptions(appctx):
    """Test dditional_descriptions property."""
    assert fails_meta({"additional_descriptions": 1})
    assert fails_meta({"additional_descriptions": {}})
    desc = {
        "description": "bla bla",
        "type": "other",
        "lang": "dan"
    }
    assert validates_meta({"additional_descriptions": [desc]})
    desc["invalid"] = "invalid"
    assert fails_meta({"additional_descriptions": [desc]})


@pytest.mark.parametrize('features', [
    [{
        "geometry": {"type": "Point", "coordinates": [6.05, 46.23333]},
    }], [{
        "identifiers": [{
            "scheme": "geonames",
            "identifier": "2661235"
        }, {
            "scheme": "tgn",
            "identifier": "http://vocab.getty.edu/tgn/8703679"
        }],
    }], [{
        "place": "CERN"
    }], [{
        "description": "Invenio birth place."
    }], [{
        "geometry": {"type": "Point", "coordinates": [6.05, 46.23333]},
        "identifiers": [{
            "scheme": "geonames",
            "identifier": "2661235"
        }, {
            "scheme": "tgn",
            "identifier": "http://vocab.getty.edu/tgn/8703679"
        }],
        "place": "CERN",
        "description": "Invenio birth place."
    }],
])
def test_locations_valid(appctx, features):
    """Test locations property.

    Note: point bounds (i.e. +-90) are checked at Marshmallow schema level.
    """
    assert validates_meta({"locations": {"features": features}})


@pytest.mark.parametrize("locations", [
    None,  # locations must be an object
    {},  # Missing features
    {'features': []},  # Empty features
    {'features': [{}]},  # Empty feature
    {
        'features': [{
            "properties": None,   # Additional props
            "place": "CERN",
        }]
    },
    {
        'features': [{
            "place": None,  # place should be a string
        }],
    },
    {
        'features': [{
            "place": "",  # place should have at least one character
        }],
    }
])
def test_locations_invalid(appctx, locations):
    assert fails_meta({"locations": locations})


def test_funding(appctx):
    """Test funding references property."""
    f = {
        "name": "European Commission",
        "identifier": "1234",
        "scheme": "ror",
    }
    a = {
        "title": "OpenAIRE",
        "number": "246686",
        "identifier": ".../246686",
        "scheme": "openaire"
    }

    assert validates_meta({"funding": [{"funder": f}]})
    assert validates_meta({"funding": [{"award": a}]})
    assert validates_meta({"funding": [{"funder": f, "award": a}]})
    # Additional props
    f["invalid"] = "test"
    assert fails_meta({"funding": [{"funder": f}]})
    a["invalid"] = "test"
    assert fails_meta({"funding": [{"award": a}]})


def test_reference(appctx):
    """Test references property."""
    assert validates_meta({"references": [
        {
            "reference": "Nielsen et al,..",
            "identifier": "101.234",
            "scheme": "doi",
        },
    ]})
    # Additional props
    assert fails_meta({"references": [
        {
            "invalid": "Nielsen et al,..",
        },
    ]})


#
# Test ext
#
def test_ext(appctx):
    """Test references property."""
    data_types = [
        "string",
        1234,
        1234.2,
        True,
        ["string"],
        [1.2],
        [False],
        ["string", -132.4, True],
    ]

    for val in data_types:
        assert validates({"ext": {"dwc": {"afield": val}}})


#
# Tombstones
#
def test_tombstones(appctx):
    """Test a tombstone."""
    assert validates({"tombstone": {
        "reason": "Spam record, removed by InvenioRDM staff.",
        "category": "spam_manual",
        "removed_by": {"user": 1},
        "timestamp": "2020-09-01T12:02:00+0000"
    }})
    assert fails({"tombstone": {
        "reason": "Spam record, removed by InvenioRDM staff.",
        "invalid": "test"
    }})


def test_no_external_resolution(appctx):
    with unittest.mock.patch('requests.get') as requests_get:
        requests_get.side_effect = AssertionError(
            "Attempted to resolve a URL using requests"
        )

        assert validates(_load_json('full-record.json'))
