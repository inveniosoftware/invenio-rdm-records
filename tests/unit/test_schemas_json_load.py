# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for Invenio RDM Records JSON Schemas."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.marshmallow.json import AffiliationSchemaV1, \
    CommunitySchemaV1, ContributorSchemaV1, CreatorSchemaV1, DateSchemaV1, \
    DescriptionSchemaV1, InternalNoteSchemaV1, LicenseSchemaV1, \
    LocationSchemaV1, MetadataSchemaV1, PointSchemaV1, ReferenceSchemaV1, \
    RelatedIdentifierSchemaV1, ResourceTypeSchemaV1, SubjectSchemaV1, \
    TitleSchemaV1


def test_community():
    """Test Community Schema."""
    valid_full = {
        "primary": "Primary Community",
        "secondary": ["Secondary Community"]
    }
    data = CommunitySchemaV1().load(valid_full)
    assert data == valid_full

    valid_primary = {
        "primary": "Primary Community"
    }
    data = CommunitySchemaV1().load(valid_primary)
    assert data == valid_primary

    invalid_no_primary = {
        "secondary": ["Secondary Community"]
    }
    with pytest.raises(ValidationError):
        CommunitySchemaV1().load(invalid_no_primary)


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


def test_contributor():
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


def test_resource_type():
    """Test resource type."""
    valid_full = {
        "type": "image",
        "subtype": "photo"
    }
    data = ResourceTypeSchemaV1().load(valid_full)
    assert data == valid_full

    valid_type = {
        "type": "image",
    }
    data = ResourceTypeSchemaV1().load(valid_type)
    assert data == valid_type

    invalid_no_type = {
        "subtype": "photo"
    }
    with pytest.raises(ValidationError):
        ResourceTypeSchemaV1().load(invalid_no_type)

    invalid_type = {
        "type": "invalid",
        "subtype": "photo"
    }
    with pytest.raises(ValidationError):
        ResourceTypeSchemaV1().load(invalid_type)

    invalid_subtype = {
        "type": "image",
        "subtype": "invalid"
    }
    with pytest.raises(ValidationError):
        ResourceTypeSchemaV1().load(invalid_subtype)


def test_title():
    """Test titles schema."""
    valid_full = {
        "title": "A Romans story",
        "type": "Other",
        "lang": "eng"
    }

    data = TitleSchemaV1().load(valid_full)
    assert data == valid_full

    valid_minimal = {
        "title": "A Romans story",
        "type": "Other"
    }

    data = TitleSchemaV1().load(valid_minimal)
    assert data == valid_minimal

    invalid_no_title = {
        "type": "Other",
        "lang": "eng"
    }
    with pytest.raises(ValidationError):
        data = TitleSchemaV1().load(invalid_no_title)

    invalid_no_title_type = {
        "title": "A Romans story",
        "lang": "eng"
    }
    with pytest.raises(ValidationError):
        data = TitleSchemaV1().load(invalid_no_title_type)

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


def test_related_identifiers():
    """Test related identifiers schema."""
    valid_full = {
        "identifier": "10.5281/zenodo.9999988",
        "scheme": "DOI",
        "relation_type": "Requires",
        "resource_type": {
            "type": "image",
            "subtype": "photo"
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
            "subtype": "photo"
        }
    }
    with pytest.raises(ValidationError):
        data = RelatedIdentifierSchemaV1().load(invalid_no_identifier)

    invalid_no_scheme = {
        "identifier": "10.5281/zenodo.9999988",
        "relation_type": "Requires",
        "resource_type": {
            "type": "image",
            "subtype": "photo"
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
            "subtype": "photo"
        }
    }
    with pytest.raises(ValidationError):
        data = RelatedIdentifierSchemaV1().load(invalid_scheme)

    invalid_no_relation_type = {
        "identifier": "10.5281/zenodo.9999988",
        "scheme": "DOI",
        "resource_type": {
            "type": "image",
            "subtype": "photo"
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
            "subtype": "photo"
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


def test_identifiers(minimal_record):
    """Test Identifiers field."""
    # Empty dict (no 'identifiers' field at all is also supported)
    minimal_record['identifiers'] = {}
    data = MetadataSchemaV1().load(minimal_record)
    assert data == minimal_record

    # Minimal
    minimal_record['identifiers'] = {
        "DOI": "10.5281/zenodo.9999999",
    }
    data = MetadataSchemaV1().load(minimal_record)
    assert data == minimal_record

    # Different schemes
    minimal_record['identifiers'] = {
        "DOI": "10.5281/zenodo.9999999",
        "ARK": "ark:/123/456",
    }
    data = MetadataSchemaV1().load(minimal_record)
    assert data == minimal_record

    # With duplicate schemes, only last one is picked
    minimal_record['identifiers'] = {
        "DOI": "10.5281/zenodo.9999999",
        "DOI": "10.5281/zenodo.0000000",
    }
    data = MetadataSchemaV1().load(minimal_record)
    assert data == minimal_record
    assert data['identifiers']['DOI'] == "10.5281/zenodo.0000000"

    # Invalid: no identifier
    minimal_record['identifiers'] = {
        "DOI": ""
    }
    with pytest.raises(ValidationError):
        data = MetadataSchemaV1().load(minimal_record)

    # Invalid: no scheme
    minimal_record['identifiers'] = {
        "": "10.5281/zenodo.9999999"
    }
    with pytest.raises(ValidationError):
        data = MetadataSchemaV1().load(minimal_record)


def test_metadata_schema(full_record, minimal_record):
    """Test metadata schema."""
    # STOPPED HERE
    # Test full attributes
    data = MetadataSchemaV1().load(full_record)
    assert data == full_record

    # Test minimal attributes
    data = MetadataSchemaV1().load(minimal_record)
    assert data == minimal_record

    # Test embargo validation
    minimal_record["embargo_date"] = "1000-01-01"
    with pytest.raises(ValidationError):
        data = MetadataSchemaV1().load(minimal_record)
