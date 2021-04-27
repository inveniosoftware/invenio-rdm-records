# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test metadata creators/contributors schemas."""

import os

import pytest
from flask_babelex import lazy_gettext as _

from invenio_rdm_records.services.schemas.metadata import ContributorSchema, \
    CreatorSchema, MetadataSchema, PersonOrOrganizationSchema

from .test_utils import assert_raises_messages


def test_creator_person_valid_minimal():
    valid_family_name = {
        "family_name": "Cesar",
        "type": "personal"
    }
    expected = {
        "family_name": "Cesar",
        "name": "Cesar",
        "type": "personal",
    }
    assert expected == PersonOrOrganizationSchema().load(valid_family_name)


def test_creator_organization_valid_minimal():
    valid_minimal = {
        "name": "Julio Cesar Empire",
        "type": "organizational"
    }
    assert valid_minimal == PersonOrOrganizationSchema().load(valid_minimal)


def test_creator_person_valid_full():
    valid_full_person = {
        "person_or_org": {
            "type": "personal",
            "given_name": "Julio",
            "family_name": "Cesar",
            "identifiers": [{
                "scheme": "orcid",
                "identifier": "0000-0002-1825-0097",
            }],
        },
        "affiliations": [{
            "name": "Entity One",
            "identifiers": [{
                "scheme": "ror",
                "identifier": "03yrm5c26"
            }]
        }]
    }

    loaded = CreatorSchema().load(valid_full_person)
    valid_full_person["person_or_org"]["name"] = "Cesar, Julio"
    assert valid_full_person == loaded


def test_creator_person_valid_no_given_name():
    valid_full_person = {
        "person_or_org": {
            "type": "personal",
            "family_name": "Cesar",
            "identifiers": [{
                "scheme": "orcid",
                "identifier": "0000-0002-1825-0097",
            }],
        },
        "affiliations": [{
            "name": "Entity One",
            "identifiers": [{
                "scheme": "ror",
                "identifier": "03yrm5c26"
            }]
        }]
    }

    loaded = CreatorSchema().load(valid_full_person)
    valid_full_person["person_or_org"]["name"] = "Cesar"
    assert valid_full_person == loaded


def test_creator_organization_valid_full():
    # Full organization
    valid_full_org = {
        "name": "California Digital Library",
        "type": "organizational",
        "identifiers": [{
            "scheme": "ror",
            "identifier": "03yrm5c26"
        }],
        "family_name": "I am ignored!"
    }

    loaded = PersonOrOrganizationSchema().load(valid_full_org)
    valid_full_org.pop("family_name")
    assert valid_full_org == loaded


def test_creatibutor_name_edge_cases():
    # Pass in name and family_name: name is ignored
    valid_person_name_and_given_name = {
        "name": "Cesar, Julio",
        "family_name": "Cesar",
        "type": "personal"
    }
    expected = {
        "name": "Cesar",
        "type": "personal",
        "family_name": "Cesar",
    }
    assert expected == PersonOrOrganizationSchema().load(
        valid_person_name_and_given_name)

    # Pass name and family_name for organization: family_name is ignored and
    # removed
    valid_org_name_and_family_name = {
        "name": "Julio Cesar Inc.",
        "family_name": "Cesar",
        "type": "organizational"
    }
    expected = {
        "name": "Julio Cesar Inc.",
        "type": "organizational",
    }
    assert expected == PersonOrOrganizationSchema().load(
        valid_org_name_and_family_name)


def test_creator_valid_role(vocabulary_clear):
    valid_role = {
        "person_or_org": {
            "family_name": "Cesar",
            "given_name": "Julio",
            "type": "personal",
        },
        "role": "rightsholder"
    }
    expected = {
        "person_or_org": {
            "family_name": "Cesar",
            "given_name": "Julio",
            "name": "Cesar, Julio",
            "type": "personal",
        },
        "role": "rightsholder"
    }
    assert expected == CreatorSchema().load(valid_role)


def test_creator_person_invalid_no_family_name():
    invalid_no_family_name = {
        "person_or_org": {
            "given_name": "Julio",
            "identifiers": [{
                "scheme": "orcid",
                "identifier": "0000-0002-1825-0097",
            }],
            "type": "personal"
        },
        "affiliations": [{
            "name": "Entity One",
            "identifiers": [{
                "scheme": "ror",
                "identifier": "03yrm5c26"
            }]
        }],
    }

    assert_raises_messages(
        lambda: CreatorSchema().load(invalid_no_family_name),
        {"person_or_org": {
            'family_name': ['Family name must be filled.']
        }}
    )


def test_creator_invalid_no_type():
    invalid_no_type = {
        "name": "Julio Cesar",
    }

    assert_raises_messages(
        lambda: PersonOrOrganizationSchema().load(invalid_no_type),
        {'type': [
            "Invalid value. Choose one of ['organizational', 'personal']."
        ]}
    )


def test_creator_invalid_type():
    invalid_type = {
        "name": "Julio Cesar",
        "type": "Invalid",
    }

    assert_raises_messages(
        lambda: PersonOrOrganizationSchema().load(invalid_type),
        {'type': [
            "Invalid value. Choose one of ['organizational', 'personal']."
        ]}
    )


def test_creator_invalid_identifiers_scheme():
    invalid_scheme = {
        "family_name": "Cesar",
        "given_name": "Julio",
        "type": "personal",
        "identifiers": [{
            "scheme": "unapproved scheme",
            "identifier": "0000-0002-1825-0097",
        }]
    }

    # Check returns the 3 schemes (org + personal)
    # because the scheme-per-type check comes later on
    loaded = PersonOrOrganizationSchema().load(invalid_scheme)
    # Check that the scheme type was force by the backend
    assert loaded["identifiers"][0]["scheme"] == "orcid"


def test_creator_invalid_identifiers_orcid():
    invalid_orcid_identifier = {
        "family_name": "Cesar",
        "given_name": "Julio",
        "type": "personal",
        "identifiers": [{
            "scheme": "orcid",
            # NOTE: This *is* an invalid ORCiD
            "identifier": "9999-9999-9999-9999",
        }]
    }

    loaded = PersonOrOrganizationSchema().load(invalid_orcid_identifier)
    # Check that the scheme type was force by the backend
    assert loaded["identifiers"][0]["scheme"] == "gnd"


def test_creator_invalid_identifiers_ror():
    invalid_ror_identifier = {
        "name": "Julio Cesar Empire",
        "type": "organizational",
        "identifiers": [{
            "scheme": "ror",
            "identifier": "9999-9999-9999-9999",
        }]
    }

    loaded = PersonOrOrganizationSchema().load(invalid_ror_identifier)
    # Check that the scheme type was force by the backend
    assert loaded["identifiers"][0]["scheme"] == "gnd"


def test_contributor_person_valid_full(vocabulary_clear):
    valid_full = {
        "affiliations": [{
            "name": "Entity One",
            "identifiers": [{
                "scheme": "ror",
                "identifier": "03yrm5c26"
            }]
        }],
        "person_or_org": {
            "family_name": "Cesar",
            "given_name": "Julio",
            "identifiers": [{
                "scheme": "orcid",
                "identifier": "0000-0002-1825-0097",
            }],
            "type": "personal",
        },
        "role": "rightsholder"
    }

    loaded = ContributorSchema().load(valid_full)
    valid_full["person_or_org"]["name"] = "Cesar, Julio"

    assert loaded == valid_full


def test_contributor_person_valid_minimal(vocabulary_clear):
    valid_minimal_family_name = {
        "person_or_org": {
            "family_name": "Cesar",
            "type": "personal",
        },
        "role": "rightsholder"
    }
    expected = {
        "person_or_org": {
            "family_name": "Cesar",
            "name": "Cesar",
            "type": "personal",
        },
        "role": "rightsholder",
    }
    assert expected == ContributorSchema().load(valid_minimal_family_name)


def test_contributor_person_invalid_no_family_name_nor_given_name(
        vocabulary_clear):
    invalid_no_family_name_nor_given_name = {
        "person_or_org": {
            "type": "personal",
            "identifiers": [{
                "scheme": "orcid",
                "identifier": "0000-0002-1825-0097",
            }],
        },
        "role": "rightsholder"
    }

    assert_raises_messages(
        lambda: ContributorSchema().load(
            invalid_no_family_name_nor_given_name
        ),
        {"person_or_org": {
            'family_name': ["Family name must be filled."]
        }}
    )


def test_contributor_invalid_no_role(vocabulary_clear):
    invalid_no_role = {
        "person_or_org": {
            "name": "Julio Cesar",
            "type": "personal",
            "given_name": "Julio",
            "family_name": "Cesar",
            "identifiers": [{
                "scheme": "orcid",
                "identifier": "0000-0002-1825-0097",
            }]
        }
    }

    assert_raises_messages(
        lambda: ContributorSchema().load(invalid_no_role),
        {'role': ['Missing data for required field.']}
    )


@pytest.fixture
def custom_config(config):
    prev_custom_vocabularies = config['RDM_RECORDS_CUSTOM_VOCABULARIES']

    config['RDM_RECORDS_CUSTOM_VOCABULARIES'] = {
        'contributors.role': {
            'path': os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'data',
                'contributor_role.csv'
            )
        }
    }

    yield config

    config['RDM_RECORDS_CUSTOM_VOCABULARIES'] = prev_custom_vocabularies


def test_contributor_invalid_role(custom_config, vocabulary_clear):
    # Doubles as a test of custom roles
    invalid_role = {
        "person_or_org": {
            "name": "Julio Cesar",
            "type": "personal",
            "given_name": "Julio",
            "family_name": "Cesar",
            "identifiers": [{
                "scheme": "orcid",
                "identifier": "0000-0002-1825-0097",
            }],
        },
        "role": "Invalid"
    }

    assert_raises_messages(
        lambda: ContributorSchema().load(invalid_role),
        {'role': [
            "Invalid value. Choose one of ['DataCollector', 'Librarian']."
        ]}
    )


def test_metadata_requires_non_empty_creators(
        minimal_metadata, vocabulary_clear):

    del minimal_metadata["creators"]
    assert_raises_messages(
        lambda: MetadataSchema().load(minimal_metadata),
        {'creators': [
            "Missing data for required field."
        ]}
    )

    minimal_metadata["creators"] = []
    assert_raises_messages(
        lambda: MetadataSchema().load(minimal_metadata),
        {'creators': [
            "Missing data for required field."
        ]}
    )

    minimal_metadata["creators"] = None
    assert_raises_messages(
        lambda: MetadataSchema().load(minimal_metadata),
        {'creators': [
            "Field may not be null."
        ]}
    )
