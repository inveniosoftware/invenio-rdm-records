# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
from contextlib import contextmanager
from pathlib import Path

import pytest
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_datastore
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.proxies import current_service as vocabulary_service

from invenio_rdm_records.fixtures.users import UsersFixture
from invenio_rdm_records.fixtures.vocabularies import GenericVocabularyEntry, \
    PrioritizedVocabulariesFixtures, VocabularyEntryWithSchemes


@pytest.fixture(scope="module")
def subjects_service(app):
    """Subjects service."""
    return current_service_registry.get("subjects")


@pytest.fixture(scope="module")
def affiliations_service(app):
    """Affiliations service."""
    return current_service_registry.get("affiliations")


def test_load_languages(app, db, es_clear):
    id_ = 'languages'
    languages = GenericVocabularyEntry(
        Path(__file__).parent / "data",
        id_,
        {
            "pid-type": "lng",
            "data-file": "vocabularies/languages.yaml"
        }
    )

    languages.load(system_identity, delay=False)

    item = vocabulary_service.read(system_identity, (id_, 'aae'))
    assert item.id == "aae"


def test_load_resource_types(app, db, es_clear):
    id_ = 'resourcetypes'
    resource_types = GenericVocabularyEntry(
        Path(__file__).parent / "data",
        id_,
        {
            "pid-type": "rsrct",
            "data-file": "vocabularies/resource_types.yaml"
        },
    )

    resource_types.load(system_identity, delay=False)

    item = vocabulary_service.read(
        system_identity,
        (id_, 'publication-annotationcollection'),
    )
    item_dict = item.to_dict()
    assert item_dict["id"] == "publication-annotationcollection"
    assert item_dict["props"]["datacite_general"] == "Collection"


def test_load_community_types(app, db, es_clear):
    id_ = 'communitytypes'
    resource_types = GenericVocabularyEntry(
        Path(__file__).parent / "data",
        id_,
        {
            "pid-type": "comtyp",
            "data-file": "vocabularies/community_types.yaml"
        },
    )

    resource_types.load(system_identity, delay=False)

    item = vocabulary_service.read(
        system_identity,
        (id_, 'organization'),
    )
    item_dict = item.to_dict()
    assert item_dict["id"] == "organization"
    assert item_dict["title"]["en"] == "Organization"


def test_loading_paths_traversal(app, db, es_clear, subjects_service):
    dir_ = Path(__file__).parent
    fixtures = PrioritizedVocabulariesFixtures(
        system_identity,
        dir_ / "app_data",
        dir_ / "data",
        "vocabularies.yaml",
        delay=False
    )

    fixtures.load()

    # app_data/vocabularies/resource_types.yaml only has image resource types
    with pytest.raises(PIDDoesNotExistError):
        vocabulary_service.read(
            system_identity,
            ('resourcetypes', 'publication-annotationcollection'),
        )

    # languages are found
    item = vocabulary_service.read(system_identity, ('languages', 'aae'))
    assert item.id == "aae"

    # Only subjects from app_data/ are loaded
    item = subjects_service.read(
        system_identity, "https://id.nlm.nih.gov/mesh/D000001")
    assert item.id == "https://id.nlm.nih.gov/mesh/D000001"
    # - subjects in extension but from already loaded scheme are not loaded
    with pytest.raises(PIDDoesNotExistError):
        subjects_service.read(
            system_identity,
            "https://id.nlm.nih.gov/mesh/D000015",
        )
    # - subjects in extension from not already loaded scheme are loaded
    item = subjects_service.read(
        system_identity, "https://id.loc.gov/authorities/subjects/sh85118623")
    assert item.id == "https://id.loc.gov/authorities/subjects/sh85118623"


@contextmanager
def filepath_replaced_by(filepath, replacement):
    backup = filepath.with_suffix(".bkp")
    filepath.replace(backup)
    replacement.replace(filepath)

    try:
        yield
    except Exception:
        raise
    finally:
        filepath.replace(replacement)
        backup.replace(filepath)


def test_reloading_paths_traversal(app, db, es_clear, subjects_service):
    dir_ = Path(__file__).parent
    fixtures = PrioritizedVocabulariesFixtures(
        system_identity,
        dir_ / "app_data",
        dir_ / "data",
        "vocabularies.yaml",
        delay=False
    )
    fixtures.load()

    # Scenario 1: Add subjects from a subject type not existing before
    # temporarily switch vocabularies.yaml.alt in app_data/
    filepath = dir_ / "app_data" / "vocabularies.yaml"
    with filepath_replaced_by(filepath, filepath.with_suffix(".alt.yaml")):
        fixtures.load()

    # Added subjects from altered vocabularies.yaml should be loaded
    item = subjects_service.read(system_identity, "310607")
    assert item.id == "310607"

    # Scenario 2: Add subjects from subject type existing before
    # temporarily switch vocabularies.yaml.alt in mock_module_A/
    filepath = dir_ / "mock_module_A/fixtures/vocabularies/vocabularies.yaml"
    with filepath_replaced_by(filepath, filepath.with_suffix(".alt.yaml")):
        fixtures.load()

    # Added subjects from altered vocabularies.yaml should be ignored
    with pytest.raises(PIDDoesNotExistError):
        subjects_service.read(system_identity, "310801")


def test_load_users(app, db, admin_role):
    dir_ = Path(__file__).parent
    users = UsersFixture(
        [
            dir_ / "app_data",
            dir_.parent.parent / "invenio_rdm_records/fixtures/data"
        ],
        "users.yaml"
    )

    users.load()

    # app_data/users.yaml doesn't create an admin@inveniosoftware.org user
    u1 = current_datastore.find_user(email="admin@inveniosoftware.org")
    assert u1 is None
    assert current_datastore.find_user(email="admin@example.com")
    assert current_datastore.find_user(email="user@example.com")


def test_load_affiliations(
        app, db, admin_role, es_clear, affiliations_service):
    dir_ = Path(__file__).parent
    affiliations = VocabularyEntryWithSchemes(
        "affiliations",
        Path(__file__).parent / "app_data",
        "affiliations",
        {
            "pid-type": "aff",
            "schemes": [{
                "id": "ROR",
                "name": "Research Organization Registry",
                "uri": "https://ror.org/",
                "data-file": "vocabularies/affiliations_ror.yaml"
            }]
        }
    )

    affiliations.load(system_identity, delay=False)

    cern = affiliations_service.read(identity=system_identity, id_="01ggx4157")
    assert cern["acronym"] == "CERN"

    with pytest.raises(PIDDoesNotExistError):
        affiliations_service.read(system_identity, "cern")
