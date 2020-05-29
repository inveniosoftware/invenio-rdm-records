# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2020 CERN.
# Copyright (C) 2019-2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for Invenio RDM Records JSON Schemas."""
import os

import pytest
from invenio_records_rest.schemas.fields import DateString, SanitizedUnicode
from marshmallow import ValidationError
from marshmallow.fields import Bool, Integer, List

from invenio_rdm_records.marshmallow.json import AffiliationSchemaV1, \
    ContributorSchemaV1, CreatorSchemaV1, DateSchemaV1, DescriptionSchemaV1, \
    InternalNoteSchemaV1, LicenseSchemaV1, LocationSchemaV1, \
    MetadataSchemaV1, PointSchemaV1, ReferenceSchemaV1, \
    RelatedIdentifierSchemaV1, ResourceTypeSchemaV1, SubjectSchemaV1, \
    TitleSchemaV1
from invenio_rdm_records.metadata_extensions import MetadataExtensions


def test_affiliations():
    """Test affiliations schema."""
    valid_full = {
        "name": "Entity One",
        "identifier": "entity-one",
        "scheme": "entity-id-scheme"
    }
    data = AffiliationSchemaV1().load(valid_full)
    assert data == valid_full

    invalid_no_name = {
        "identifier": "entity-one",
        "scheme": "entity-id-scheme"
    }
    with pytest.raises(ValidationError):
        data = AffiliationSchemaV1().load(invalid_no_name)

    invalid_no_identifier = {
        "name": "Entity One",
        "scheme": "entity-id-scheme"
    }
    with pytest.raises(ValidationError):
        data = AffiliationSchemaV1().load(invalid_no_identifier)

    invalid_no_scheme = {
        "name": "Entity One",
        "identifier": "entity-one"
    }
    with pytest.raises(ValidationError):
        data = AffiliationSchemaV1().load(invalid_no_scheme)


def test_creator():
    """Test creator schema."""
    # If present, bare minimum
    valid_minimal = {
        "name": "Julio Cesar",
        "type": "Personal"
    }

    data = CreatorSchemaV1().load(valid_minimal)

    assert data == valid_minimal

    # Full person
    valid_full_person = {
        "name": "Julio Cesar",
        "type": "Personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "9999-9999-9999-9999",
        },
        "affiliations": [{
            "name": "Entity One",
            "identifier": "entity-one",
            "scheme": "entity-id-scheme"
        }]
    }

    data = CreatorSchemaV1().load(valid_full_person)

    assert data == valid_full_person

    # Full organization
    valid_full_org = {
        "name": "California Digital Library",
        "type": "Organizational",
        "identifiers": {
            "ROR": "03yrm5c26",
        },
        # "given_name", "family_name" and "affiliations" are ignored if passed
        "family_name": "I am ignored!"
    }

    data = CreatorSchemaV1().load(valid_full_org)

    assert data == valid_full_org

    invalid_no_name = {
        "type": "Personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "9999-9999-9999-9999",
        },
        "affiliations": [{
            "name": "Entity One",
            "identifier": "entity-one",
            "scheme": "entity-id-scheme"
        }]
    }
    with pytest.raises(ValidationError):
        data = CreatorSchemaV1().load(invalid_no_name)

    invalid_no_type = {
        "name": "Julio Cesar",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "9999-9999-9999-9999",
        },
        "affiliations": [{
            "name": "Entity One",
            "identifier": "entity-one",
            "scheme": "entity-id-scheme"
        }]
    }
    with pytest.raises(ValidationError):
        data = CreatorSchemaV1().load(invalid_no_type)

    invalid_type = {
        "name": "Julio Cesar",
        "type": "Invalid",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "9999-9999-9999-9999",
        },
        "affiliations": [{
            "name": "Entity One",
            "identifier": "entity-one",
            "scheme": "entity-id-scheme"
        }]
    }
    with pytest.raises(ValidationError):
        data = CreatorSchemaV1().load(invalid_type)


def test_contributor(vocabulary_clear):
    """Test contributor schema."""
    valid_full = {
        "name": "Julio Cesar",
        "type": "Personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "9999-9999-9999-9999",
        },
        "affiliations": [{
            "name": "Entity One",
            "identifier": "entity-one",
            "scheme": "entity-id-scheme"
        }],
        "role": "RightsHolder"
    }

    data = ContributorSchemaV1().load(valid_full)
    assert data == valid_full

    valid_minimal = {
        "name": "Julio Cesar",
        "type": "Personal",
        "role": "RightsHolder"
    }

    data = ContributorSchemaV1().load(valid_minimal)
    assert data == valid_minimal

    invalid_no_name = {
        "type": "Personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "9999-9999-9999-9999",
        },
        "affiliations": [{
            "name": "Entity One",
            "identifier": "entity-one",
            "scheme": "entity-id-scheme"
        }],
        "role": "RightsHolder"
    }
    with pytest.raises(ValidationError):
        data = ContributorSchemaV1().load(invalid_no_name)

    invalid_no_name_type = {
        "name": "Julio Cesar",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "9999-9999-9999-9999",
        },
        "affiliations": [{
            "name": "Entity One",
            "identifier": "entity-one",
            "scheme": "entity-id-scheme"
        }],
        "role": "RightsHolder"
    }
    with pytest.raises(ValidationError):
        data = ContributorSchemaV1().load(invalid_no_name_type)

    invalid_name_type = {
        "name": "Julio Cesar",
        "type": "Invalid",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "9999-9999-9999-9999",
        },
        "affiliations": [{
            "name": "Entity One",
            "identifier": "entity-one",
            "scheme": "entity-id-scheme"
        }],
        "role": "RightsHolder"
    }
    with pytest.raises(ValidationError):
        data = ContributorSchemaV1().load(invalid_name_type)

    invalid_no_role = {
        "name": "Julio Cesar",
        "type": "Personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "9999-9999-9999-9999",
        },
        "affiliations": [{
            "name": "Entity One",
            "identifier": "entity-one",
            "scheme": "entity-id-scheme"
        }]
    }
    with pytest.raises(ValidationError):
        data = ContributorSchemaV1().load(invalid_no_role)

    invalid_role = {
        "name": "Julio Cesar",
        "type": "Personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "9999-9999-9999-9999",
        },
        "affiliations": [{
            "name": "Entity One",
            "identifier": "entity-one",
            "scheme": "entity-id-scheme"
        }],
        "role": "Invalid"
    }
    with pytest.raises(ValidationError):
        data = ContributorSchemaV1().load(invalid_role)


def test_custom_contributor_role(config, vocabulary_clear):
    """Test custom contributor role."""
    prev_config = config['RDM_RECORDS_CUSTOM_VOCABULARIES']
    config['RDM_RECORDS_CUSTOM_VOCABULARIES'] = {
        'contributors.role': {
            'path': os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'data',
                'contributor_role.csv'
            )
        }
    }

    # new contributor role validates
    librarian_role = {
        "name": "Julio Cesar",
        "type": "Personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "9999-9999-9999-9999",
        },
        "affiliations": [{
            "name": "Entity One",
            "identifier": "entity-one",
            "scheme": "entity-id-scheme"
        }],
        "role": "Librarian"
    }
    data = ContributorSchemaV1().load(librarian_role)
    assert data == librarian_role

    # old contributor role does not validate
    contactperson_role = {
        "name": "Julio Cesar",
        "type": "Personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "9999-9999-9999-9999",
        },
        "affiliations": [{
            "name": "Entity One",
            "identifier": "entity-one",
            "scheme": "entity-id-scheme"
        }],
        "role": "ContactPerson"
    }
    with pytest.raises(ValidationError):
        data = ContributorSchemaV1().load(contactperson_role)

    config['RDM_RECORDS_CUSTOM_VOCABULARIES'] = prev_config


def test_internal_note():
    """Test internal note schema."""
    valid_full = {
        "user": "inveniouser",
        "note": "RDM record",
        "timestamp": "2020-02-01"
    }
    data = InternalNoteSchemaV1().load(valid_full)
    assert data == valid_full

    invalid_no_user = {
        "note": "RDM record",
        "timestamp": "2020-02-01"
    }
    with pytest.raises(ValidationError):
        data = InternalNoteSchemaV1().load(invalid_no_user)

    invalid_no_note = {
        "user": "inveniouser",
        "timestamp": "2020-02-01"
    }
    with pytest.raises(ValidationError):
        data = InternalNoteSchemaV1().load(invalid_no_note)

    invalid_no_timestamp = {
        "user": "inveniouser",
        "note": "RDM record"
    }
    with pytest.raises(ValidationError):
        data = InternalNoteSchemaV1().load(invalid_no_timestamp)

    invalid_timestamp = {
        "user": "inveniouser",
        "note": "RDM record",
        "timestamp": "01/02/2020"
    }
    with pytest.raises(ValidationError):
        data = InternalNoteSchemaV1().load(invalid_timestamp)


def test_resource_type(vocabulary_clear):
    """Test resource type."""
    valid_full = {
        "type": "image",
        "subtype": "image-photo"
    }
    data = ResourceTypeSchemaV1().load(valid_full)
    assert data == valid_full

    valid_no_subtype = {
        "type": "poster"
    }
    data = ResourceTypeSchemaV1().load(valid_no_subtype)
    assert data == valid_no_subtype

    invalid_no_subtype_when_required = {
        "type": "image"
    }
    with pytest.raises(ValidationError):
        ResourceTypeSchemaV1().load(invalid_no_subtype_when_required)

    invalid_no_type = {
        "subtype": "image-photo"
    }
    with pytest.raises(ValidationError):
        ResourceTypeSchemaV1().load(invalid_no_type)

    invalid_type = {
        "type": "invalid",
        "subtype": "image-photo"
    }
    with pytest.raises(ValidationError):
        ResourceTypeSchemaV1().load(invalid_type)

    invalid_subtype = {
        "type": "image",
        "subtype": "invalid"
    }
    with pytest.raises(ValidationError):
        ResourceTypeSchemaV1().load(invalid_subtype)


def test_custom_resource_type(config, vocabulary_clear):
    """Test custom resource type."""
    config['RDM_RECORDS_CUSTOM_VOCABULARIES'] = {
        'resource_type': {
            'path': os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'data',
                'resource_types.csv'
            )
        }
    }

    # new resource type validates
    valid_full = {
        "type": "my_image",
        "subtype": "my_photo"
    }
    data = ResourceTypeSchemaV1().load(valid_full)
    assert data == valid_full

    # old resource type does not validate
    valid_full = {
        "type": "image",
        "subtype": "image-photo"
    }
    with pytest.raises(ValidationError):
        data = ResourceTypeSchemaV1().load(valid_full)

    config['RDM_RECORDS_CUSTOM_VOCABULARIES'] = {}


def test_title(vocabulary_clear):
    """Test titles schema."""
    valid_full = {
        "title": "A Romans story",
        "type": "Other",
        "lang": "eng"
    }
    data = TitleSchemaV1().load(valid_full)
    assert data == valid_full

    valid_partial = {
        "title": "A Romans story",
        "lang": "eng"
    }
    data = TitleSchemaV1().load(valid_partial)
    assert data == dict(valid_partial, type='MainTitle')

    valid_minimal = {
        "title": "A Romans story",
    }
    data = TitleSchemaV1().load(valid_minimal)
    assert data == dict(valid_minimal, type='MainTitle')

    invalid_no_title = {
        "type": "Other",
        "lang": "eng"
    }
    with pytest.raises(ValidationError):
        data = TitleSchemaV1().load(invalid_no_title)

    invalid_title_type = {
        "title": "A Romans story",
        "type": "Invalid",
        "lang": "eng"
    }
    with pytest.raises(ValidationError):
        data = TitleSchemaV1().load(invalid_title_type)

    invalid_lang = {
        "title": "A Romans story",
        "type": "Other",
        "lang": "inv"
    }
    with pytest.raises(ValidationError):
        data = TitleSchemaV1().load(invalid_lang)


def test_description():
    """Test descriptions schema."""
    valid_full = {
        "description": "A story on how Julio Cesar relates to Gladiator.",
        "type": "Abstract",
        "lang": "eng"
    }

    data = DescriptionSchemaV1().load(valid_full)
    assert data == valid_full

    valid_minimal = {
        "description": "A story on how Julio Cesar relates to Gladiator.",
        "type": "Abstract"
    }

    data = DescriptionSchemaV1().load(valid_minimal)
    assert data == valid_minimal

    invalid_no_description = {
        "type": "Abstract",
        "lang": "eng"
    }
    with pytest.raises(ValidationError):
        data = DescriptionSchemaV1().load(invalid_no_description)

    invalid_no_description_type = {
        "description": "A story on how Julio Cesar relates to Gladiator.",
        "lang": "eng"
    }
    with pytest.raises(ValidationError):
        data = DescriptionSchemaV1().load(invalid_no_description_type)

    invalid_description_type = {
        "description": "A story on how Julio Cesar relates to Gladiator.",
        "type": "Invalid",
        "lang": "eng"
    }
    with pytest.raises(ValidationError):
        data = DescriptionSchemaV1().load(invalid_description_type)

    invalid_lang = {
        "description": "A story on how Julio Cesar relates to Gladiator.",
        "type": "Abstract",
        "lang": "inv"
    }
    with pytest.raises(ValidationError):
        data = DescriptionSchemaV1().load(invalid_lang)


def test_license():
    """Test license scehma."""
    valid_full = {
        "license": "Copyright Maximo Decimo Meridio 2020. Long statement",
        "uri": "https://opensource.org/licenses/BSD-3-Clause",
        "identifier": "BSD-3",
        "scheme": "BSD-3"
    }

    data = LicenseSchemaV1().load(valid_full)
    assert data == valid_full

    valid_minimal = {
        "license": "Copyright Maximo Decimo Meridio 2020. Long statement"
    }

    data = LicenseSchemaV1().load(valid_minimal)
    assert data == valid_minimal

    invalid_no_license = {
        "uri": "https://opensource.org/licenses/BSD-3-Clause",
        "identifier": "BSD-3",
        "scheme": "BSD-3"
    }
    with pytest.raises(ValidationError):
        data = LicenseSchemaV1().load(invalid_no_license)


def test_subject():
    """Test subject schema."""
    valid_full = {
        "subject": "Romans",
        "identifier": "subj-1",
        "scheme": "no-scheme"
    }

    data = SubjectSchemaV1().load(valid_full)
    assert data == valid_full

    valid_minimal = {
        "subject": "Romans"
    }

    data = SubjectSchemaV1().load(valid_minimal)
    assert data == valid_minimal

    invalid_no_subject = {
        "identifier": "subj-1",
        "scheme": "no-scheme"
    }
    with pytest.raises(ValidationError):
        data = SubjectSchemaV1().load(invalid_no_subject)


def test_date():
    """Test date schama."""
    valid_full = {
        "start": "2020-06-01",
        "end":  "2021-06-01",
        "description": "Random test date",
        "type": "Other"
    }

    data = DateSchemaV1().load(valid_full)
    assert data == valid_full

    # Note that none start or end are required. But it validates that at
    # least one of them is present.
    valid_minimal = {
        "start": "2020-06-01",
        "type": "Other"
    }

    data = DateSchemaV1().load(valid_minimal)
    assert data == valid_minimal

    invalid_no_type = {
        "start": "2020-06-01",
        "end":  "2021-06-01",
        "description": "Random test date",
    }
    with pytest.raises(ValidationError):
        data = DateSchemaV1().load(invalid_no_type)

    invalid_end_format = {
        "start": "2020/06/01",
        "end":  "2021-06-01",
        "description": "Random test date",
    }
    with pytest.raises(ValidationError):
        data = DateSchemaV1().load(invalid_end_format)

    invalid_end_format = {
        "start": "2020-06-01",
        "end":  "2021-13-01",  # Days and months swaped
        "description": "Random test date",
    }
    with pytest.raises(ValidationError):
        data = DateSchemaV1().load(invalid_end_format)


def test_related_identifiers(vocabulary_clear):
    """Test related identifiers schema."""
    valid_full = {
        "identifier": "10.5281/zenodo.9999988",
        "scheme": "DOI",
        "relation_type": "Requires",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        }
    }

    data = RelatedIdentifierSchemaV1().load(valid_full)
    assert data == valid_full

    valid_minimal = {
        "identifier": "10.5281/zenodo.9999988",
        "scheme": "DOI",
        "relation_type": "Requires"
    }

    data = RelatedIdentifierSchemaV1().load(valid_minimal)
    assert data == valid_minimal

    invalid_no_identifier = {
        "scheme": "DOI",
        "relation_type": "Requires",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        }
    }
    with pytest.raises(ValidationError):
        data = RelatedIdentifierSchemaV1().load(invalid_no_identifier)

    invalid_no_scheme = {
        "identifier": "10.5281/zenodo.9999988",
        "relation_type": "Requires",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        }
    }
    with pytest.raises(ValidationError):
        data = RelatedIdentifierSchemaV1().load(invalid_no_scheme)

    invalid_scheme = {
        "identifier": "10.5281/zenodo.9999988",
        "scheme": "INVALID",
        "relation_type": "Requires",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        }
    }
    with pytest.raises(ValidationError):
        data = RelatedIdentifierSchemaV1().load(invalid_scheme)

    invalid_no_relation_type = {
        "identifier": "10.5281/zenodo.9999988",
        "scheme": "DOI",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        }
    }
    with pytest.raises(ValidationError):
        data = RelatedIdentifierSchemaV1().load(invalid_no_relation_type)

    invalid_relation_type = {
        "identifier": "10.5281/zenodo.9999988",
        "scheme": "DOI",
        "relation_type": "INVALID",
        "resource_type": {
            "type": "image",
            "subtype": "image-photo"
        }
    }
    with pytest.raises(ValidationError):
        data = RelatedIdentifierSchemaV1().load(invalid_relation_type)


def test_references():
    """Test references schema."""
    valid_full = {
        "reference_string": "Reference to something et al.",
        "identifier": "9999.99988",
        "scheme": "GRID"
    }

    data = ReferenceSchemaV1().load(valid_full)
    assert data == valid_full

    valid_minimal = {
        "reference_string": "Reference to something et al."
    }

    data = ReferenceSchemaV1().load(valid_minimal)
    assert data == valid_minimal

    invalid_no_reference = {
        "identifier": "9999.99988",
        "scheme": "GRID"
    }
    with pytest.raises(ValidationError):
        data = ReferenceSchemaV1().load(invalid_no_reference)

    invalid_scheme = {
        "reference_string": "Reference to something et al.",
        "identifier": "9999.99988",
        "scheme": "Invalid"
    }
    with pytest.raises(ValidationError):
        data = ReferenceSchemaV1().load(invalid_scheme)


def test_point():
    """Test point."""
    valid_full = {
        "lat": 41.902604,
        "lon": 12.496189
    }

    data = PointSchemaV1().load(valid_full)
    assert data == valid_full

    invalid_no_lat = {
        "lon": 12.496189
    }
    with pytest.raises(ValidationError):
        data = PointSchemaV1().load(invalid_no_lat)

    invalid_no_lon = {
        "lat": 41.902604,
    }
    with pytest.raises(ValidationError):
        data = PointSchemaV1().load(invalid_no_lon)


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

    data = LocationSchemaV1().load(valid_full)
    assert data == valid_full

    valid_minimal = {
        "place": "Rome",
    }

    data = LocationSchemaV1().load(valid_minimal)
    assert data == valid_minimal

    invalid_no_place = {
        "point": {
            "lat": 41.902604,
            "lon": 12.496189
        },
        "description": "Rome, from Romans"
    }
    with pytest.raises(ValidationError):
        data = LocationSchemaV1().load(invalid_no_place)


def test_identifiers(minimal_input_record):
    """Test Identifiers field."""
    # No 'identifiers' field at all is supported
    data = MetadataSchemaV1().load(minimal_input_record)
    assert data.get('identifiers') == minimal_input_record.get('identifiers')

    # Empty dict
    minimal_input_record['identifiers'] = {}
    data = MetadataSchemaV1().load(minimal_input_record)
    assert data['identifiers'] == minimal_input_record['identifiers']

    # Minimal
    minimal_input_record['identifiers'] = {
        "DOI": "10.5281/zenodo.9999999",
    }
    data = MetadataSchemaV1().load(minimal_input_record)
    assert data['identifiers'] == minimal_input_record['identifiers']

    # Different schemes
    minimal_input_record['identifiers'] = {
        "DOI": "10.5281/zenodo.9999999",
        "ARK": "ark:/123/456",
    }
    data = MetadataSchemaV1().load(minimal_input_record)
    assert data['identifiers'] == minimal_input_record['identifiers']

    # With duplicate schemes, only last one is picked
    minimal_input_record['identifiers'] = {
        "DOI": "10.5281/zenodo.9999999",
        "DOI": "10.5281/zenodo.0000000",
    }
    data = MetadataSchemaV1().load(minimal_input_record)
    assert data['identifiers'] == minimal_input_record['identifiers']
    assert data['identifiers']['DOI'] == "10.5281/zenodo.0000000"

    # Invalid: no identifier
    minimal_input_record['identifiers'] = {
        "DOI": ""
    }
    with pytest.raises(ValidationError):
        data = MetadataSchemaV1().load(minimal_input_record)

    # Invalid: no scheme
    minimal_input_record['identifiers'] = {
        "": "10.5281/zenodo.9999999"
    }
    with pytest.raises(ValidationError):
        data = MetadataSchemaV1().load(minimal_input_record)


def test_extensions():
    """Test metadata extensions schema."""
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

    extensions = MetadataExtensions(
        RDM_RECORDS_METADATA_NAMESPACES,
        RDM_RECORDS_METADATA_EXTENSIONS
    )
    ExtensionsSchema = extensions.to_schema()

    # Minimal if not absent
    valid_minimal = {
        'dwc:family': 'Felidae'
    }

    data = ExtensionsSchema().load(valid_minimal)

    assert data == valid_minimal

    # Full
    valid_full = {
        'dwc:family': 'Felidae',
        'dwc:behavior': 'Plays with yarn, sleeps in cardboard box.',
        'nubiomed:number_in_sequence': 3,
        'nubiomed:scientific_sequence': [1, 1, 2, 3, 5, 8],
        'nubiomed:original_presentation_date': '2019-02-14',
        'nubiomed:right_or_wrong': True,
    }

    data = ExtensionsSchema().load(valid_full)

    assert data == valid_full

    # Invalid
    invalid_number_in_sequence = {
        'dwc:family': 'Felidae',
        'nubiomed:scientific_sequence': [1, 'l', 2, 3, 5, 8],
    }
    with pytest.raises(ValidationError):
        data = ExtensionsSchema().load(invalid_number_in_sequence)


def test_publication_date(
        vocabulary_clear, minimal_input_record, minimal_record):
    def assert_publication_dates(data, expected):
        assert data['publication_date'] == expected_record['publication_date']
        assert (
            data['_publication_date_search'] ==
            expected_record['_publication_date_search']
        )

    expected_record = minimal_record

    # No publication_date uses today as default
    data = MetadataSchemaV1().load(minimal_input_record)

    assert_publication_dates(data, expected_record)

    # Falsey publication_date uses today as default
    minimal_input_record['publication_date'] = ""

    data = MetadataSchemaV1().load(minimal_input_record)

    assert_publication_dates(data, expected_record)

    # Partial
    minimal_input_record['publication_date'] = '2020-02'
    expected_record['publication_date'] = '2020-02'
    expected_record['_publication_date_search'] = '2020-02-01'

    data = MetadataSchemaV1().load(minimal_input_record)

    assert_publication_dates(data, expected_record)

    # Interval (asymmetrical is allowed!)
    minimal_input_record['publication_date'] = '2020-02-02/2025-12'
    expected_record['publication_date'] = '2020-02-02/2025-12'
    expected_record['_publication_date_search'] = '2020-02-02'

    data = MetadataSchemaV1().load(minimal_input_record)

    assert_publication_dates(data, expected_record)

    # Invalid date
    minimal_input_record['publication_date'] = 'invalid'
    with pytest.raises(ValidationError):
        data = MetadataSchemaV1().load(minimal_input_record)

    # Invalid interval
    minimal_input_record['publication_date'] = '2025-12/2020-02-02'
    with pytest.raises(ValidationError):
        data = MetadataSchemaV1().load(minimal_input_record)


def test_embargo_date(vocabulary_clear, minimal_input_record):
    # Test embargo validation
    minimal_input_record["embargo_date"] = "1000-01-01"
    with pytest.raises(ValidationError):
        data = MetadataSchemaV1().load(minimal_input_record)


def test_metadata_schema(
        vocabulary_clear, full_input_record, full_record,
        minimal_input_record, minimal_record):
    """Test metadata schema."""
    # Test full attributes
    data = MetadataSchemaV1().load(full_input_record)
    assert data == full_record

    # Test minimal attributes
    data = MetadataSchemaV1().load(minimal_input_record)
    assert data == minimal_record
