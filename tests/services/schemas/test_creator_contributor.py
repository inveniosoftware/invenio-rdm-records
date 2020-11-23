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


def test_creator_person_valid_minimal():
    valid_given_name = {
        "given_name": "Julio",
        "type": "personal"
    }
    expected = {
        "given_name": "Julio",
        "name": "Julio",
        "type": "personal",
    }
    assert expected == CreatorSchema().load(valid_given_name)

    valid_family_name = {
        "family_name": "Cesar",
        "type": "personal"
    }
    expected = {
        "family_name": "Cesar",
        "name": "Cesar",
        "type": "personal",
    }
    assert expected == CreatorSchema().load(valid_family_name)


def test_creator_organization_valid_minimal():
    valid_minimal = {
        "name": "Julio Cesar Empire",
        "type": "organizational"
    }
    assert valid_minimal == CreatorSchema().load(valid_minimal)


def test_creator_person_valid_full():
    valid_full_person = {
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
    expected = {
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

    assert expected == CreatorSchema().load(valid_full_person)


def test_creator_organization_valid_full():
    # Full organization
    valid_full_org = {
        "name": "California Digital Library",
        "type": "organizational",
        "identifiers": {
            "ror": "03yrm5c26",
        },
        "family_name": "I am ignored!"
    }
    expected = {
        "name": "California Digital Library",
        "type": "organizational",
        "identifiers": {
            "ror": "03yrm5c26",
        },
    }
    assert expected == CreatorSchema().load(valid_full_org)


def test_creatibutor_name_edge_cases():
    # Pass in name and given_name: name is ignored
    valid_person_name_and_given_name = {
        "name": "Cesar, Julio",
        "given_name": "Julio",
        "type": "personal"
    }
    expected = {
        "name": "Julio",
        "type": "personal",
        "given_name": "Julio",
    }
    assert expected == CreatorSchema().load(valid_person_name_and_given_name)

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
    assert expected == CreatorSchema().load(valid_org_name_and_family_name)


def test_creator_valid_role(vocabulary_clear):
    valid_role = {
        "family_name": "Cesar",
        "given_name": "Julio",
        "type": "personal",
        "role": "rightsholder"
    }
    expected = {
        "family_name": "Cesar",
        "given_name": "Julio",
        "name": "Cesar, Julio",
        "type": "personal",
        "role": "rightsholder"
    }
    assert expected == CreatorSchema().load(valid_role)


def test_creator_person_invalid_no_given_name_nor_family_name():
    invalid_no_given_name_nor_family_name = {
        "affiliations": [{
            "name": "Entity One",
            "identifiers": {
                "ror": "03yrm5c26"
            }
        }],
        "identifiers": {
            "orcid": "0000-0002-1825-0097",
        },
        "type": "personal",
    }

    assert_raises_messages(
        lambda: CreatorSchema().load(invalid_no_given_name_nor_family_name),
        {
            'given_name': ['One name must be filled.'],
            'family_name': ['One name must be filled.']
        }
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
        "family_name": "Cesar",
        "given_name": "Julio",
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
        "family_name": "Cesar",
        "given_name": "Julio",
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


def test_creator_person_invalid_identifiers():
    invalid_identifier_for_person = {
        "family_name": "Cesar",
        "given_name": "Julio",
        "type": "personal",
        "identifiers": {
            "ror": "03yrm5c26"
        }
    }

    assert_raises_messages(
        lambda: CreatorSchema().load(invalid_identifier_for_person),
        {'identifiers': ["Invalid value. Choose one of ['orcid']."]}
    )


def test_creator_organization_invalid_identifiers():
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


def test_contributor_person_valid_full(vocabulary_clear):
    valid_full = {
        "affiliations": [{
            "name": "Entity One",
            "identifiers": {
                "ror": "03yrm5c26"
            }
        }],
        "family_name": "Cesar",
        "given_name": "Julio",
        "identifiers": {
            "orcid": "0000-0002-1825-0097",
        },
        "type": "personal",
        "role": "rightsholder"
    }
    expected = {**valid_full, "name": "Cesar, Julio"}
    assert expected == ContributorSchema().load(valid_full)


def test_contributor_person_valid_minimal(vocabulary_clear):
    valid_minimal_given_name = {
        "given_name": "Julio",
        "type": "personal",
        "role": "rightsholder"
    }
    expected = {
        "given_name": "Julio",
        "name": "Julio",
        "type": "personal",
        "role": "rightsholder",
    }
    assert expected == ContributorSchema().load(valid_minimal_given_name)

    valid_minimal_family_name = {
        "family_name": "Cesar",
        "type": "personal",
        "role": "rightsholder"
    }
    expected = {
        "family_name": "Cesar",
        "name": "Cesar",
        "type": "personal",
        "role": "rightsholder",
    }
    assert expected == ContributorSchema().load(valid_minimal_family_name)


def test_contributor_person_invalid_no_family_name_nor_given_name(
        vocabulary_clear):
    invalid_no_family_name_nor_given_name = {
        "type": "personal",
        "identifiers": {
            "orcid": "0000-0002-1825-0097",
        },
        "role": "rightsholder"
    }

    assert_raises_messages(
        lambda: ContributorSchema().load(
            invalid_no_family_name_nor_given_name
        ),
        {
            'family_name': ['One name must be filled.'],
            'given_name': ['One name must be filled.'],
        }
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
