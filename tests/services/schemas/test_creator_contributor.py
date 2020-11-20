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
    CreatorSchema

from .test_utils import assert_raises_messages


def test_creator_valid_minimal_person():
    valid_minimal = {
        "name": "Cesar, Julio",
        "type": "personal"
    }
    expected = {
        "name": "Cesar, Julio",
        "type": "personal",
        "given_name": "Julio",
        "family_name": "Cesar",

    }
    assert expected == CreatorSchema().load(valid_minimal)


def test_creator_valid_minimal_organization():
    valid_minimal = {
        "name": "Cesar, Julio",
        "type": "organizational"
    }
    assert valid_minimal == CreatorSchema().load(valid_minimal)


def test_creator_valid_full_person():
    valid_full_person = {
        "name": "Cesar, Julio",
        "type": "personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "orcid": '0000-0002-1825-0097',
        },
        "affiliations": [{
            "name": "Entity One",
            "identifiers": {
                "ror": "03yrm5c26"
            }
        }]
    }
    assert valid_full_person == CreatorSchema().load(valid_full_person)


def test_creator_valid_full_organization():
    # Full organization
    valid_full_org = {
        "name": "California Digital Library",
        "type": "organizational",
        "identifiers": {
            "ror": "03yrm5c26",
        },
        # "given_name", "family_name" and "affiliations" are allowed but
        # meaningless. Perhaps disallow them?
        "family_name": "I am ignored!"
    }
    data = CreatorSchema().load(valid_full_org)
    assert data == valid_full_org


def test_creatibutor_name_edge_cases():
    # More than 1 comma
    valid_many_commas = {
        "name": "Cesar, Julio, Chavez",
        "type": "personal"
    }
    expected = {
        "name": "Cesar, Julio, Chavez",
        "type": "personal",
        "given_name": "Julio, Chavez",
        "family_name": "Cesar",
    }
    assert expected == CreatorSchema().load(valid_many_commas)

    # No comma
    valid_no_comma = {
        "name": "Cesar Julio",
        "type": "personal"
    }
    expected = {
        "name": "Cesar Julio",
        "type": "personal",
        "given_name": "",
        "family_name": "Cesar Julio",

    }
    assert expected == CreatorSchema().load(valid_no_comma)

    # Given name is also explicitly passed
    valid_explicit_given_name = {
        "name": "Cesar, Julio",
        "type": "personal",
        "given_name": "Julius",
    }
    expected = {
        "name": "Cesar, Julio",
        "type": "personal",
        "given_name": "Julius",  # overrode Julio
        "family_name": "Cesar",
    }
    assert expected == CreatorSchema().load(valid_explicit_given_name)


def test_creator_valid_role(vocabulary_clear):
    valid_minimal = {
        "name": "Cesar, Julio",
        "type": "personal",
        "role": "rightsholder"
    }
    expected = {
        "name": "Cesar, Julio",
        "type": "personal",
        "role": "rightsholder",
        "family_name": "Cesar",
        "given_name": "Julio",
    }
    assert expected == CreatorSchema().load(valid_minimal)


def test_creator_invalid_no_name():
    invalid_no_name = {
        "type": "personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "orcid": "0000-0002-1825-0097",
        },
        "affiliations": [{
            "name": "Entity One",
            "identifiers": {
                "ror": "03yrm5c26"
            }
        }]
    }

    assert_raises_messages(
        lambda: CreatorSchema().load(invalid_no_name),
        {'name': ['Missing data for required field.']}
    )


def test_creator_invalid_no_type():
    invalid_no_type = {
        "name": "Julio Cesar",
    }

    assert_raises_messages(
        lambda: CreatorSchema().load(invalid_no_type),
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
        lambda: CreatorSchema().load(invalid_type),
        {'type': [
            "Invalid value. Choose one of ['organizational', 'personal']."
        ]}
    )


def test_creator_invalid_identifiers_scheme():
    invalid_scheme = {
        "name": "Julio Cesar",
        "type": "personal",
        "identifiers": {
            "unapproved scheme": "0000-0002-1825-0097",
        }
    }

    assert_raises_messages(
        lambda: CreatorSchema().load(invalid_scheme),
        {'identifiers': ["Invalid value. Choose one of ['orcid', 'ror']."]}
    )


def test_creator_invalid_identifiers_orcid():
    invalid_orcid_identifier = {
        "name": "Julio Cesar",
        "type": "personal",
        "identifiers": {
            # NOTE: This *is* an invalid ORCiD
            "orcid": "9999-9999-9999-9999",
        }
    }

    assert_raises_messages(
        lambda: CreatorSchema().load(invalid_orcid_identifier),
        {'identifiers': {'orcid': ["Invalid value."]}}
    )


def test_creator_invalid_identifiers_ror():
    invalid_ror_identifier = {
        "name": "Julio Cesar Empire",
        "type": "organizational",
        "identifiers": {
            "ror": "9999-9999-9999-9999",
        }
    }

    assert_raises_messages(
        lambda: CreatorSchema().load(invalid_ror_identifier),
        {'identifiers': {'ror': ["Invalid value."]}}
    )


def test_creator_invalid_identifiers_for_person():
    invalid_identifier_for_person = {
        "name": "Julio Cesar",
        "type": "personal",
        "identifiers": {
            "ror": "03yrm5c26"
        }
    }

    assert_raises_messages(
        lambda: CreatorSchema().load(invalid_identifier_for_person),
        {'identifiers': ["Invalid value. Choose one of ['orcid']."]}
    )


def test_creator_invalid_identifiers_for_org():
    invalid_identifier_for_org = {
        "name": "Julio Cesar Empire",
        "type": "organizational",
        "identifiers": {
            "orcid": "0000-0002-1825-0097",
        }
    }

    assert_raises_messages(
        lambda: CreatorSchema().load(invalid_identifier_for_org),
        {'identifiers': ["Invalid value. Choose one of ['ror']."]}
    )


def test_contributor_valid_full(vocabulary_clear):
    valid_full = {
        "name": "Julio Cesar",
        "type": "personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "orcid": "0000-0002-1825-0097",
        },
        "affiliations": [{
            "name": "Entity One",
            "identifiers": {
                "ror": "03yrm5c26"
            }
        }],
        "role": "rightsholder"
    }
    assert valid_full == ContributorSchema().load(valid_full)


def test_contributor_valid_minimal(vocabulary_clear):
    valid_minimal = {
        "name": "Cesar, Julio",
        "type": "personal",
        "role": "rightsholder"
    }
    expected = {
        "name": "Cesar, Julio",
        "type": "personal",
        "role": "rightsholder",
        "family_name": "Cesar",
        "given_name": "Julio",
    }
    assert expected == ContributorSchema().load(valid_minimal)


def test_contributor_invalid_no_name(vocabulary_clear):
    invalid_no_name = {
        "type": "personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "orcid": "0000-0002-1825-0097",
        },
        "role": "rightsholder"
    }

    assert_raises_messages(
        lambda: ContributorSchema().load(invalid_no_name),
        {'name': ['Missing data for required field.']}
    )


def test_contributor_invalid_no_role(vocabulary_clear):
    invalid_no_role = {
        "name": "Julio Cesar",
        "type": "personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "orcid": "0000-0002-1825-0097",
        },
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
        "name": "Julio Cesar",
        "type": "personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "orcid": "0000-0002-1825-0097",
        },
        "role": "Invalid"
    }

    assert_raises_messages(
        lambda: ContributorSchema().load(invalid_role),
        {'role': [
            "Invalid value. Choose one of ['DataCollector', 'Librarian']."
        ]}
    )
