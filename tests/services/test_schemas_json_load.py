# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
# Copyright (C) 2019-2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DEPRECATED. Tests for Invenio RDM Records JSON Schemas."""
import pytest
from invenio_records_rest.schemas.fields import DateString, SanitizedUnicode
from marshmallow import ValidationError
from marshmallow.fields import Bool, Integer, List

from invenio_rdm_records.services.schemas.metadata import ContributorSchema, \
    CreatorSchema, DateSchema, DescriptionSchema, InternalNoteSchema, \
    LicenseSchema, LocationSchema, MetadataSchema, PointSchema, \
    ReferenceSchema, RelatedIdentifierSchema, ResourceTypeSchema, \
    SubjectSchema
from invenio_rdm_records.services.schemas.metadata_extensions import \
    MetadataExtensions


def test_internal_note():
    """Test internal note schema."""
    valid_full = {
        "user": "inveniouser",
        "note": "RDM record",
        "timestamp": "2020-02-01"
    }
    data = InternalNoteSchema().load(valid_full)
    assert data == valid_full

    invalid_no_user = {
        "note": "RDM record",
        "timestamp": "2020-02-01"
    }
    with pytest.raises(ValidationError):
        data = InternalNoteSchema().load(invalid_no_user)

    invalid_no_note = {
        "user": "inveniouser",
        "timestamp": "2020-02-01"
    }
    with pytest.raises(ValidationError):
        data = InternalNoteSchema().load(invalid_no_note)

    invalid_no_timestamp = {
        "user": "inveniouser",
        "note": "RDM record"
    }
    with pytest.raises(ValidationError):
        data = InternalNoteSchema().load(invalid_no_timestamp)

    invalid_timestamp = {
        "user": "inveniouser",
        "note": "RDM record",
        "timestamp": "01/02/2020"
    }
    with pytest.raises(ValidationError):
        data = InternalNoteSchema().load(invalid_timestamp)


def test_license():
    """Test license scehma."""
    valid_full = {
        "license": "Copyright Maximo Decimo Meridio 2020. Long statement",
        "uri": "https://opensource.org/licenses/BSD-3-Clause",
        "identifier": "BSD-3",
        "scheme": "BSD-3"
    }

    data = LicenseSchema().load(valid_full)
    assert data == valid_full

    valid_minimal = {
        "license": "Copyright Maximo Decimo Meridio 2020. Long statement"
    }

    data = LicenseSchema().load(valid_minimal)
    assert data == valid_minimal

    invalid_no_license = {
        "uri": "https://opensource.org/licenses/BSD-3-Clause",
        "identifier": "BSD-3",
        "scheme": "BSD-3"
    }
    with pytest.raises(ValidationError):
        data = LicenseSchema().load(invalid_no_license)


def test_related_identifiers(vocabulary_clear):
    """Test related identifiers schema."""
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

    valid_minimal = {
        "identifier": "10.5281/zenodo.9999988",
        "scheme": "doi",
        "relation_type": "requires"
    }

    data = RelatedIdentifierSchema().load(valid_minimal)
    assert data == valid_minimal

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

    invalid_no_scheme = {
        "identifier": "10.5281/zenodo.9999988",
        "relation_type": "requires",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        }
    }
    with pytest.raises(ValidationError):
        data = RelatedIdentifierSchema().load(invalid_no_scheme)

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


def test_references():
    """Test references schema."""
    valid_full = {
        "reference": "Reference to something et al.",
        "identifier": "9999.99988",
        "scheme": "grid"
    }

    data = ReferenceSchema().load(valid_full)
    assert data == valid_full

    valid_minimal = {
        "reference": "Reference to something et al."
    }

    data = ReferenceSchema().load(valid_minimal)
    assert data == valid_minimal

    invalid_no_reference = {
        "identifier": "9999.99988",
        "scheme": "grid"
    }
    with pytest.raises(ValidationError):
        data = ReferenceSchema().load(invalid_no_reference)

    invalid_scheme = {
        "reference": "Reference to something et al.",
        "identifier": "9999.99988",
        "scheme": "Invalid"
    }
    with pytest.raises(ValidationError):
        data = ReferenceSchema().load(invalid_scheme)


def test_point():
    """Test point."""
    valid_full = {
        "lat": 41.902604,
        "lon": 12.496189
    }

    data = PointSchema().load(valid_full)
    assert data == valid_full

    invalid_no_lat = {
        "lon": 12.496189
    }
    with pytest.raises(ValidationError):
        data = PointSchema().load(invalid_no_lat)

    invalid_no_lon = {
        "lat": 41.902604,
    }
    with pytest.raises(ValidationError):
        data = PointSchema().load(invalid_no_lon)


def test_location():
    """Test location schema."""
    valid_full = {
        "point": {
            "lat": 41.902604,
            "lon": 12.496189
        },
        "place": "Rome",
        "description": "Rome, from Romans"
    }

    data = LocationSchema().load(valid_full)
    assert data == valid_full

    valid_minimal = {
        "place": "Rome",
    }

    data = LocationSchema().load(valid_minimal)
    assert data == valid_minimal

    invalid_no_place = {
        "point": {
            "lat": 41.902604,
            "lon": 12.496189
        },
        "description": "Rome, from Romans"
    }
    with pytest.raises(ValidationError):
        data = LocationSchema().load(invalid_no_place)


@pytest.mark.skip()
def test_extensions(app, minimal_record):
    """Test metadata extensions schema."""
    # Setup metadata extensions
    RDM_RECORDS_METADATA_NAMESPACES = {
        'dwc': {
            '@context': 'https://example.com/dwc/terms'
        },
        'nubiomed': {
            '@context': 'https://example.com/nubiomed/terms'
        }
    }

    RDM_RECORDS_METADATA_EXTENSIONS = {
        'dwc:family': {
            'elasticsearch': 'keyword',
            'marshmallow': SanitizedUnicode(required=True)
        },
        'dwc:behavior': {
            'elasticsearch': 'text',
            'marshmallow': SanitizedUnicode()
        },
        'nubiomed:number_in_sequence': {
            'elasticsearch': 'long',
            'marshmallow': Integer()
        },
        'nubiomed:scientific_sequence': {
            'elasticsearch': 'long',
            'marshmallow': List(Integer())
        },
        'nubiomed:original_presentation_date': {
            'elasticsearch': 'date',
            'marshmallow': DateString()
        },
        'nubiomed:right_or_wrong': {
            'elasticsearch': 'boolean',
            'marshmallow': Bool()
        }
    }

    orig_metadata_extensions = (
        app.extensions['invenio-rdm-records'].metadata_extensions
    )

    app.extensions['invenio-rdm-records'].metadata_extensions = (
        MetadataExtensions(
            RDM_RECORDS_METADATA_NAMESPACES,
            RDM_RECORDS_METADATA_EXTENSIONS
        )
    )

    # Minimal if not absent
    valid_minimal = {
        'dwc:family': 'Felidae'
    }
    minimal_record['extensions'] = valid_minimal
    data = MetadataSchema().load(minimal_record)
    assert valid_minimal == data.get('extensions')

    # Full
    valid_full = {
        'dwc:family': 'Felidae',
        'dwc:behavior': 'Plays with yarn, sleeps in cardboard box.',
        'nubiomed:number_in_sequence': 3,
        'nubiomed:scientific_sequence': [1, 1, 2, 3, 5, 8],
        'nubiomed:original_presentation_date': '2019-02-14',
        'nubiomed:right_or_wrong': True,
    }
    minimal_record['extensions'] = valid_full
    data = MetadataSchema().load(minimal_record)
    assert valid_full == data.get('extensions')

    # Invalid
    invalid_number_in_sequence = {
        'dwc:family': 'Felidae',
        'nubiomed:scientific_sequence': [1, 'l', 2, 3, 5, 8],
    }
    minimal_record['extensions'] = invalid_number_in_sequence
    with pytest.raises(ValidationError):
        data = MetadataSchema().load(minimal_record)

    app.extensions['invenio-rdm-records'].metadata_extensions = (
        orig_metadata_extensions
    )


def test_embargo_date(vocabulary_clear, minimal_record):
    # Test embargo validation
    minimal_record["embargo_date"] = "1000-01-01"
    with pytest.raises(ValidationError):
        data = MetadataSchema().load(minimal_record)


@pytest.mark.skip()
def test_metadata_schema(
        vocabulary_clear, full_record, minimal_record):
    """Test metadata schema."""
    # Test full attributes
    data = MetadataSchema().load(full_record)
    assert data == full_record

    # Test minimal attributes
    data = MetadataSchema().load(minimal_record)
    assert data == minimal_record
