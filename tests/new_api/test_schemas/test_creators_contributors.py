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

from invenio_rdm_records.schemas.metadata import ContributorSchemaV1, \
    CreatorSchemaV1

from .test_utils import assert_raises_messages


def test_creator_valid_minimal():
    valid_minimal = {
        "name": "Julio Cesar",
        "type": "Personal"
    }
    assert valid_minimal == CreatorSchemaV1().load(valid_minimal)


def test_creator_valid_full_person():
    valid_full_person = {
        "name": "Julio Cesar",
        "type": "Personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": '0000-0002-1825-0097',
        },
        "affiliations": [{
            "name": "Entity One",
            "identifiers": {
                "ror": "03yrm5c26"
            }
        }]
    }
    data = CreatorSchemaV1().load(valid_full_person)
    assert data == valid_full_person


def test_creator_valid_full_organization():
    # Full organization
    valid_full_org = {
        "name": "California Digital Library",
        "type": "Organizational",
        "identifiers": {
            "ror": "03yrm5c26",
        },
        # "given_name", "family_name" and "affiliations" are ignored if passed
        "family_name": "I am ignored!"
    }
    data = CreatorSchemaV1().load(valid_full_org)
    assert data == valid_full_org


def test_creator_invalid_no_name():
    invalid_no_name = {
        "type": "Personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "0000-0002-1825-0097",
        },
        "affiliations": [{
            "name": "Entity One",
            "identifiers": {
                "ror": "03yrm5c26"
            }
        }]
    }

    assert_raises_messages(
        lambda: CreatorSchemaV1().load(invalid_no_name),
        {'name': ['Missing data for required field.']}
    )


def test_creator_invalid_no_type():
    invalid_no_type = {
        "name": "Julio Cesar",
    }

    assert_raises_messages(
        lambda: CreatorSchemaV1().load(invalid_no_type),
        {'type': ['Missing data for required field.']}
    )


def test_creator_invalid_type():
    invalid_type = {
        "name": "Julio Cesar",
        "type": "Invalid",
    }

    assert_raises_messages(
        lambda: CreatorSchemaV1().load(invalid_type),
        {'type': [
            "Invalid value. Choose one of ['Organizational', 'Personal']."
        ]}
    )


def test_creator_invalid_identifiers_scheme():
    invalid_scheme = {
        "name": "Julio Cesar",
        "type": "Personal",
        "identifiers": {
            "unapproved scheme": "0000-0002-1825-0097",
        }
    }

    assert_raises_messages(
        lambda: CreatorSchemaV1().load(invalid_scheme),
        {'identifiers': ["Invalid value. Choose one of ['Orcid', 'ror']."]}
    )


def test_creator_invalid_identifiers_orcid():
    invalid_orcid_identifier = {
        "name": "Julio Cesar",
        "type": "Personal",
        "identifiers": {
            # NOTE: This *is* an invalid ORCiD
            "Orcid": "9999-9999-9999-9999",
        }
    }

    assert_raises_messages(
        lambda: CreatorSchemaV1().load(invalid_orcid_identifier),
        {'identifiers': {'Orcid': ["Invalid value."]}}
    )


def test_creator_invalid_identifiers_ror():
    invalid_ror_identifier = {
        "name": "Julio Cesar Empire",
        "type": "Organizational",
        "identifiers": {
            "ror": "9999-9999-9999-9999",
        }
    }

    assert_raises_messages(
        lambda: CreatorSchemaV1().load(invalid_ror_identifier),
        {'identifiers': {'ror': ["Invalid value."]}}
    )


def test_creator_invalid_identifiers_for_person():
    invalid_identifier_for_person = {
        "name": "Julio Cesar",
        "type": "Personal",
        "identifiers": {
            "ror": "03yrm5c26"
        }
    }

    assert_raises_messages(
        lambda: CreatorSchemaV1().load(invalid_identifier_for_person),
        {'identifiers': ["Invalid value. Choose one of ['Orcid']."]}
    )


def test_creator_invalid_identifiers_for_org():
    invalid_identifier_for_org = {
        "name": "Julio Cesar Empire",
        "type": "Organizational",
        "identifiers": {
            "Orcid": "0000-0002-1825-0097",
        }
    }

    assert_raises_messages(
        lambda: CreatorSchemaV1().load(invalid_identifier_for_org),
        {'identifiers': ["Invalid value. Choose one of ['ror']."]}
    )


def test_contributor_valid_full(vocabulary_clear):
    valid_full = {
        "name": "Julio Cesar",
        "type": "Personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "0000-0002-1825-0097",
        },
        "affiliations": [{
            "name": "Entity One",
            "identifiers": {
                "ror": "03yrm5c26"
            }
        }],
        "role": "RightsHolder"
    }
    assert valid_full == ContributorSchemaV1().load(valid_full)


def test_contributor_valid_minimal(vocabulary_clear):
    valid_minimal = {
        "name": "Julio Cesar",
        "type": "Personal",
        "role": "RightsHolder"
    }
    assert valid_minimal == ContributorSchemaV1().load(valid_minimal)


def test_contributor_invalid_no_name(vocabulary_clear):
    invalid_no_name = {
        "type": "Personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "0000-0002-1825-0097",
        },
        "role": "RightsHolder"
    }

    assert_raises_messages(
        lambda: ContributorSchemaV1().load(invalid_no_name),
        {'name': ['Missing data for required field.']}
    )


def test_contributor_invalid_no_role(vocabulary_clear):
    invalid_no_role = {
        "name": "Julio Cesar",
        "type": "Personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "0000-0002-1825-0097",
        },
    }

    assert_raises_messages(
        lambda: ContributorSchemaV1().load(invalid_no_role),
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
        "type": "Personal",
        "given_name": "Julio",
        "family_name": "Cesar",
        "identifiers": {
            "Orcid": "0000-0002-1825-0097",
        },
        "role": "Invalid"
    }

    assert_raises_messages(
        lambda: ContributorSchemaV1().load(invalid_role),
        {'role': [
            "Invalid value. Choose one of ['DataCollector', 'Librarian']."
        ]}
    )
