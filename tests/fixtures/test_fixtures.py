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

from invenio_rdm_records.fixtures.affiliations import AffiliationsFixture
from invenio_rdm_records.fixtures.users import UsersFixture
from invenio_rdm_records.fixtures.vocabularies import \
    PrioritizedVocabulariesFixtures, SingleVocabularyEntry


def test_load_languages(app, db):
    id_ = 'languages'
    languages = SingleVocabularyEntry(
        Path(__file__).parent,
        id_,
        {
            "pid-type": "lng",
            "data-file": "data/vocabularies/languages.yaml"
        }
    )

    languages.load(system_identity, delay=False)

    item = vocabulary_service.read((id_, 'aae'), system_identity)
    assert item.id == "aae"


def test_load_resource_types(app, db):
    id_ = 'resourcetypes'
    resource_types = SingleVocabularyEntry(
        Path(__file__).parent,
        id_,
        {
            "pid-type": "rsrct",
            "data-file": "data/vocabularies/resource_types.yaml"
        }
    )

    resource_types.load(system_identity, delay=False)

    item = vocabulary_service.read(
        (id_, 'publication-annotationcollection'),
        system_identity
    )
    item_dict = item.to_dict()
    assert item_dict["id"] == "publication-annotationcollection"
    assert item_dict["props"]["datacite_general"] == "Collection"


def test_loading_paths_traversal(app, db):
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
            ('resourcetypes', 'publication-annotationcollection'),
            system_identity
        )

    # languages are found
    item = vocabulary_service.read(('languages', 'aae'), system_identity)
    assert item.id == "aae"

    # Only subjects A from app_data/ are loaded
    item = vocabulary_service.read(('subjects', 'A-D000008'), system_identity)
    assert item.id == "A-D000008"
    with pytest.raises(PIDDoesNotExistError):
        vocabulary_service.read(
            ('subjects', 'A-D000015'),
            system_identity
        )

    # subjects B from an extension are loaded
    item = vocabulary_service.read(('subjects', 'B-D000008'), system_identity)
    assert item.id == "B-D000008"


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


def test_reloading_paths_traversal(app, db):
    dir_ = Path(__file__).parent
    fixtures = PrioritizedVocabulariesFixtures(
        system_identity,
        dir_ / "app_data",
        dir_ / "data",
        "vocabularies.yaml",
        delay=False
    )
    fixtures.load()

    # Scenario 1: added subject type not existing before, so should be loaded
    # temporarily switch vocabularies.yaml.alt in app_data/
    filepath = dir_ / "app_data" / "vocabularies.yaml"
    with filepath_replaced_by(filepath, filepath.with_suffix(".yaml.alt")):
        fixtures.load()

    # subjects C from altered vocabularies.yaml are loaded
    item = vocabulary_service.read(('subjects', 'C-D000008'), system_identity)
    assert item.id == "C-D000008"

    # Scenario 2: added subject type existing before, so should be ignored
    # temporarily switch vocabularies.yaml.alt in mock_module_A/
    filepath = dir_ / "mock_module_A/fixtures/vocabularies/vocabularies.yaml"
    with filepath_replaced_by(filepath, filepath.with_suffix(".yaml.alt")):
        fixtures.load()

    # subjects C from altered vocabularies.yaml are ignored
    # 'C-D000015' is only present in vocabularies.yaml.alt of mock_module_A/
    with pytest.raises(PIDDoesNotExistError):
        vocabulary_service.read(
            ('subjects', 'C-D000015'),
            system_identity
        )


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


def test_load_affiliations(app, db, admin_role):
    dir_ = Path(__file__).parent
    affiliations = AffiliationsFixture(
        [
            dir_ / "app_data",
            dir_.parent.parent / "invenio_rdm_records/fixtures/data"
        ],
        "affiliations.yaml"
    )

    affiliations.load()

    # app_data/users.yaml doesn't create an admin@inveniosoftware.org user
    service = current_service_registry.get("rdm-affiliations")
    cern = service.read(identity=system_identity, id_="01ggx4157")
    assert cern["acronym"] == "CERN"
    pytest.raises(PIDDoesNotExistError, service.read, "cern", system_identity)
