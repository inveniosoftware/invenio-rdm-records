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

from invenio_rdm_records.services.schemas.metadata import (
    ContributorSchema,
    CreatorSchema,
    MetadataSchema,
    PersonOrOrganizationSchema,
)

from .test_utils import assert_raises_messages


def test_creator_person_valid_minimal(app):
    valid_family_name = {"family_name": "Cesar", "type": "personal"}
    expected = {
        "family_name": "Cesar",
        "name": "Cesar",
        "type": "personal",
    }
    assert expected == PersonOrOrganizationSchema().load(valid_family_name)


def test_creator_organization_valid_minimal(app):
    valid_minimal = {"name": "Julio Cesar Empire", "type": "organizational"}
    assert valid_minimal == PersonOrOrganizationSchema().load(valid_minimal)


def test_creator_person_valid_full(app):
    valid_full_person = {
        "person_or_org": {
            "type": "personal",
            "given_name": "Julio",
            "family_name": "Cesar",
            "identifiers": [
                {
                    "scheme": "orcid",
                    "identifier": "0000-0002-1825-0097",
                }
            ],
        },
        "affiliations": [{"id": "test"}],
    }

    loaded = CreatorSchema().load(valid_full_person)
    valid_full_person["person_or_org"]["name"] = "Cesar, Julio"
    assert valid_full_person == loaded


def test_creator_person_valid_no_given_name(app):
    valid_full_person = {
        "person_or_org": {
            "type": "personal",
            "family_name": "Cesar",
            "identifiers": [
                {
                    "scheme": "orcid",
                    "identifier": "0000-0002-1825-0097",
                }
            ],
        },
        "affiliations": [{"id": "test"}],
    }

    loaded = CreatorSchema().load(valid_full_person)
    valid_full_person["person_or_org"]["name"] = "Cesar"
    assert valid_full_person == loaded


def test_creator_organization_valid_full(app):
    # Full organization
    valid_full_org = {
        "name": "California Digital Library",
        "type": "organizational",
        "identifiers": [{"scheme": "ror", "identifier": "03yrm5c26"}],
        "family_name": "I am ignored!",
    }

    loaded = PersonOrOrganizationSchema().load(valid_full_org)
    valid_full_org.pop("family_name")
    assert valid_full_org == loaded


def test_creatibutor_name_edge_cases(app):
    # Pass in name and family_name: name is ignored
    valid_person_name_and_given_name = {
        "name": "Cesar, Julio",
        "family_name": "Cesar",
        "type": "personal",
    }
    expected = {
        "name": "Cesar",
        "type": "personal",
        "family_name": "Cesar",
    }
    assert expected == PersonOrOrganizationSchema().load(
        valid_person_name_and_given_name
    )

    # Pass name and family_name for organization: family_name is ignored and
    # removed
    valid_org_name_and_family_name = {
        "name": "Julio Cesar Inc.",
        "family_name": "Cesar",
        "type": "organizational",
    }
    expected = {
        "name": "Julio Cesar Inc.",
        "type": "organizational",
    }
    assert expected == PersonOrOrganizationSchema().load(valid_org_name_and_family_name)


def test_creator_valid_role(app):
    valid_role = {
        "person_or_org": {
            "family_name": "Cesar",
            "given_name": "Julio",
            "type": "personal",
        },
        "role": {"id": "editor"},
    }
    expected = {
        "person_or_org": {
            "family_name": "Cesar",
            "given_name": "Julio",
            "name": "Cesar, Julio",
            "type": "personal",
        },
        "role": {"id": "editor"},
    }
    assert expected == CreatorSchema().load(valid_role)


def test_creator_person_invalid_no_family_name(app):
    invalid_no_family_name = {
        "person_or_org": {
            "given_name": "Julio",
            "identifiers": [
                {
                    "scheme": "orcid",
                    "identifier": "0000-0002-1825-0097",
                }
            ],
            "type": "personal",
        },
        "affiliations": [{"id": "test"}],
    }

    assert_raises_messages(
        lambda: CreatorSchema().load(invalid_no_family_name),
        {"person_or_org": {"family_name": ["Family name cannot be blank."]}},
    )


def test_creator_invalid_no_type(app):
    invalid_no_type = {
        "name": "Julio Cesar",
    }

    assert_raises_messages(
        lambda: PersonOrOrganizationSchema().load(invalid_no_type),
        {"type": ["Invalid value. Choose one of ['organizational', 'personal']."]},
    )


def test_creator_invalid_type(app):
    invalid_type = {
        "name": "Julio Cesar",
        "type": "Invalid",
    }

    assert_raises_messages(
        lambda: PersonOrOrganizationSchema().load(invalid_type),
        {"type": ["Invalid value. Choose one of ['organizational', 'personal']."]},
    )


def test_creator_invalid_identifiers_scheme(app):
    invalid_scheme = {
        "family_name": "Cesar",
        "given_name": "Julio",
        "type": "personal",
        "identifiers": [
            {
                "scheme": "unapproved scheme",
                "identifier": "0000-0002-1825-0097",
            }
        ],
    }

    # Check returns the 3 schemes (org + personal)
    # because the scheme-per-type check comes later on
    assert_raises_messages(
        lambda: PersonOrOrganizationSchema().load(invalid_scheme),
        {"identifiers": {0: {"scheme": "Invalid scheme."}}},
    )


def test_creator_invalid_identifiers_orcid(app):
    invalid_orcid_identifier = {
        "family_name": "Cesar",
        "given_name": "Julio",
        "type": "personal",
        "identifiers": [
            {
                "scheme": "orcid",
                # NOTE: This *is* an invalid ORCiD
                "identifier": "9999-9999-9999-9999",
            }
        ],
    }

    assert_raises_messages(
        lambda: PersonOrOrganizationSchema().load(invalid_orcid_identifier),
        {"identifiers": {0: {"identifier": "Invalid ORCID identifier."}}},
    )


def test_creator_invalid_identifiers_ror(app):
    invalid_ror_identifier = {
        "name": "Julio Cesar Empire",
        "type": "organizational",
        "identifiers": [
            {
                "scheme": "ror",
                "identifier": "9999-9999-9999-9999",
            }
        ],
    }

    assert_raises_messages(
        lambda: PersonOrOrganizationSchema().load(invalid_ror_identifier),
        {"identifiers": {0: {"identifier": "Invalid ROR identifier."}}},
    )


def test_contributor_person_valid_full(app):
    valid_full = {
        "affiliations": [{"id": "test"}],
        "person_or_org": {
            "family_name": "Cesar",
            "given_name": "Julio",
            "identifiers": [
                {
                    "scheme": "orcid",
                    "identifier": "0000-0002-1825-0097",
                }
            ],
            "type": "personal",
        },
        "role": {"id": "rightsholder"},
    }

    loaded = ContributorSchema().load(valid_full)
    valid_full["person_or_org"]["name"] = "Cesar, Julio"

    assert loaded == valid_full


def test_contributor_person_valid_minimal(app):
    valid_minimal_family_name = {
        "person_or_org": {
            "family_name": "Cesar",
            "type": "personal",
        },
        "role": {"id": "rightsholder"},
    }
    expected = {
        "person_or_org": {
            "family_name": "Cesar",
            "name": "Cesar",
            "type": "personal",
        },
        "role": {"id": "rightsholder"},
    }
    assert expected == ContributorSchema().load(valid_minimal_family_name)


def test_contributor_person_invalid_no_family_name_nor_given_name(app):
    invalid_no_family_name_nor_given_name = {
        "person_or_org": {
            "type": "personal",
            "identifiers": [
                {
                    "scheme": "orcid",
                    "identifier": "0000-0002-1825-0097",
                }
            ],
        },
        "role": {"id": "rightsholder"},
    }

    assert_raises_messages(
        lambda: ContributorSchema().load(invalid_no_family_name_nor_given_name),
        {"person_or_org": {"family_name": ["Family name cannot be blank."]}},
    )


def test_contributor_invalid_no_role(app):
    invalid_no_role = {
        "person_or_org": {
            "name": "Julio Cesar",
            "type": "personal",
            "given_name": "Julio",
            "family_name": "Cesar",
            "identifiers": [
                {
                    "scheme": "orcid",
                    "identifier": "0000-0002-1825-0097",
                }
            ],
        }
    }

    assert_raises_messages(
        lambda: ContributorSchema().load(invalid_no_role),
        {"role": ["Missing data for required field."]},
    )


def test_contributor_invalid_role(app):
    # Doubles as a test of custom roles
    invalid_role = {
        "person_or_org": {
            "name": "Julio Cesar",
            "type": "personal",
            "given_name": "Julio",
            "family_name": "Cesar",
            "identifiers": [
                {
                    "scheme": "orcid",
                    "identifier": "0000-0002-1825-0097",
                }
            ],
        },
        "role": "Invalid",
    }

    assert_raises_messages(
        lambda: ContributorSchema().load(invalid_role),
        {"role": {"_schema": ["Invalid input type."]}},
    )


def test_metadata_requires_non_empty_creators(app, minimal_metadata):
    del minimal_metadata["creators"]
    assert_raises_messages(
        lambda: MetadataSchema().load(minimal_metadata),
        {"creators": ["Missing data for required field."]},
    )

    minimal_metadata["creators"] = []
    assert_raises_messages(
        lambda: MetadataSchema().load(minimal_metadata),
        {"creators": ["Missing data for required field."]},
    )

    minimal_metadata["creators"] = None
    assert_raises_messages(
        lambda: MetadataSchema().load(minimal_metadata),
        {"creators": ["Field may not be null."]},
    )
