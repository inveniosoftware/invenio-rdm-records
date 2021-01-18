# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test identifier schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import MetadataSchema, \
    RelatedIdentifierSchema


def test_valid_related_identifiers():
    valid_full = {
        "identifier": "10.5281/zenodo.9999988",
        "scheme": "doi",
        "relation_type": "requires",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        }
    }

    data = RelatedIdentifierSchema().load(valid_full)
    assert data == valid_full


def test_valid_minimal_related_identifiers():
    valid_minimal = {
        "identifier": "10.5281/zenodo.9999988",
        "scheme": "doi",
        "relation_type": "requires"
    }

    data = RelatedIdentifierSchema().load(valid_minimal)
    assert data == valid_minimal


def test_valid_no_scheme_related_identifiers(app):
    """It is valid becuase the schema is detected by the schema."""
    valid_no_scheme = {
        "identifier": "10.5281/zenodo.9999988",
        "relation_type": "requires",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        }
    }
    loaded = RelatedIdentifierSchema().load(valid_no_scheme)
    valid_no_scheme["scheme"] = "doi"
    assert valid_no_scheme == loaded


def test_invalid_no_identifiers_related_identifiers(app):
    invalid_no_identifier = {
        "scheme": "doi",
        "relation_type": "requires",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        }
    }
    with pytest.raises(ValidationError):
        data = RelatedIdentifierSchema().load(invalid_no_identifier)


def test_invalid_scheme_related_identifiers(app):
    invalid_scheme = {
        "identifier": "10.5281/zenodo.9999988",
        "scheme": "INVALID",
        "relation_type": "requires",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        }
    }
    with pytest.raises(ValidationError):
        data = RelatedIdentifierSchema().load(invalid_scheme)


def test_invalid_no_type_related_identifiers(app):
    invalid_no_relation_type = {
        "identifier": "10.5281/zenodo.9999988",
        "scheme": "doi",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        }
    }
    with pytest.raises(ValidationError):
        data = RelatedIdentifierSchema().load(invalid_no_relation_type)


def test_invalid_relation_type_related_identifiers(app):
    invalid_relation_type = {
        "identifier": "10.5281/zenodo.9999988",
        "scheme": "doi",
        "relation_type": "INVALID",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        }
    }
    with pytest.raises(ValidationError):
        data = RelatedIdentifierSchema().load(invalid_relation_type)


def test_invalid_extra_field_related_identifiers(app):
    invalid_extra = {
        "identifier": "10.5281/zenodo.9999988",
        "scheme": "doi",
        "relation_type": "INVALID",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        },
        "extra": "field"
    }
    with pytest.raises(ValidationError):
        data = RelatedIdentifierSchema().load(invalid_extra)


def test_valid_related_identifiers_in_schema(app, minimal_record):
    metadata = minimal_record['metadata']
    metadata['related_identifiers'] = [
        {
            "identifier": "10.5281/zenodo.9999988",
            "scheme": "doi",
            "relation_type": "requires",
            "resource_type": {
                "type": "image",
                "subtype": "image-photo"
            }
        }, {
            "identifier": "10.5281/zenodo.9999977",
            "scheme": "doi",
            "relation_type": "requires"
        }
    ]
    data = MetadataSchema().load(metadata)['related_identifiers']
    assert metadata['related_identifiers'] == data


def test_invalid_related_identifiers(app, minimal_record):
    metadata = minimal_record['metadata']
    metadata['related_identifiers'] = {
        "identifier": "10.5281/zenodo.9999988",
        "scheme": "doi",
        "relation_type": "requires",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        }
    }

    with pytest.raises(ValidationError):
        data = MetadataSchema().load(metadata)
