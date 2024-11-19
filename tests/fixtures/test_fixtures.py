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
from invenio_communities import current_communities
from invenio_communities.fixtures.tasks import create_demo_community
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.proxies import current_service as vocabulary_service
from sqlalchemy.exc import NoResultFound

from invenio_rdm_records.fixtures import RecordsFixture, create_demo_record
from invenio_rdm_records.fixtures.communities import CommunitiesFixture
from invenio_rdm_records.fixtures.users import UsersFixture
from invenio_rdm_records.fixtures.vocabularies import (
    GenericVocabularyEntry,
    PrioritizedVocabulariesFixtures,
    VocabularyEntry,
)
from invenio_rdm_records.proxies import current_rdm_records


@pytest.fixture(scope="module")
def subjects_service(app):
    """Subjects service."""
    return current_service_registry.get("subjects")


@pytest.fixture(scope="module")
def affiliations_service(app):
    """Affiliations service."""
    return current_service_registry.get("affiliations")


def test_load_languages(app, db, search_clear):
    id_ = "languages"
    languages = GenericVocabularyEntry(
        Path(__file__).parent / "data",
        id_,
        {"pid-type": "lng", "data-file": "vocabularies/languages.yaml"},
    )

    languages.load(system_identity, delay=False)

    item = vocabulary_service.read(system_identity, (id_, "aae"))
    assert item.id == "aae"


def test_load_resource_types(app, db, search_clear):
    id_ = "resourcetypes"
    resource_types = GenericVocabularyEntry(
        Path(__file__).parent / "data",
        id_,
        {"pid-type": "rsrct", "data-file": "vocabularies/resource_types.yaml"},
    )

    resource_types.load(system_identity, delay=False)

    item = vocabulary_service.read(
        system_identity,
        (id_, "publication-annotationcollection"),
    )
    item_dict = item.to_dict()
    assert item_dict["id"] == "publication-annotationcollection"
    assert item_dict["props"]["datacite_general"] == "Collection"


def test_load_community_types(app, db, search_clear):
    id_ = "communitytypes"
    resource_types = GenericVocabularyEntry(
        Path(__file__).parent / "data",
        id_,
        {"pid-type": "comtyp", "data-file": "vocabularies/community_types.yaml"},
    )

    resource_types.load(system_identity, delay=False)

    item = vocabulary_service.read(
        system_identity,
        (id_, "organization"),
    )
    item_dict = item.to_dict()
    assert item_dict["id"] == "organization"
    assert item_dict["title"]["en"] == "Organization"


def test_loading_paths_traversal(app, db, search_clear, subjects_service):
    dir_ = Path(__file__).parent
    fixtures = PrioritizedVocabulariesFixtures(
        system_identity,
        dir_ / "app_data",
        dir_ / "data",
        "vocabularies.yaml",
        delay=False,
    )

    fixtures.load()

    # app_data/vocabularies/resource_types.yaml only has image resource types
    with pytest.raises(PIDDoesNotExistError):
        vocabulary_service.read(
            system_identity,
            ("resourcetypes", "publication-annotationcollection"),
        )

    # languages are found
    item = vocabulary_service.read(system_identity, ("languages", "aae"))
    assert item.id == "aae"

    # Only subjects from app_data/ are loaded
    item = subjects_service.read(system_identity, "https://id.nlm.nih.gov/mesh/D000001")
    assert item.id == "https://id.nlm.nih.gov/mesh/D000001"
    # - subjects in extension but from already loaded scheme are not loaded
    with pytest.raises(PIDDoesNotExistError):
        subjects_service.read(
            system_identity,
            "https://id.nlm.nih.gov/mesh/D000015",
        )
    # - subjects in extension from not already loaded scheme are loaded
    item = subjects_service.read(
        system_identity, "https://id.loc.gov/authorities/subjects/sh85118623"
    )
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


def test_reloading_paths_traversal(app, db, search_clear, subjects_service):
    dir_ = Path(__file__).parent
    fixtures = PrioritizedVocabulariesFixtures(
        system_identity,
        dir_ / "app_data",
        dir_ / "data",
        "vocabularies.yaml",
        delay=False,
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
        [dir_ / "app_data", dir_.parent.parent / "invenio_rdm_records/fixtures/data"],
        "users.yaml",
    )

    users.load()

    # app_data/users.yaml doesn't create an admin@inveniosoftware.org user
    non_existing_user = current_datastore.find_user(email="admin@inveniosoftware.org")
    admin = current_datastore.find_user(email="admin@example.com")
    user = current_datastore.find_user(email="user@example.com")

    assert non_existing_user is None

    assert admin
    assert admin.confirmed_at

    assert user
    assert user.confirmed_at is None


def test_load_communities(app, db, location):
    dir_ = Path(__file__).parent
    service = current_communities.service
    communities = CommunitiesFixture(
        [dir_ / "app_data", dir_.parent.parent / "invenio_rdm_records/fixtures/data"],
        "communities.yaml",
        create_demo_community,
        dir_ / "app_data" / "img",
        delay=False,
    )

    communities.load()

    # Refresh to make changes live
    service.record_cls.index.refresh()

    community1 = service.search(system_identity, q=f"slug:community1")
    community2 = service.search(system_identity, q=f"slug:community2")

    assert community1.total == 1
    assert community2.total == 1

    community1_id = list(community1.hits)[0]["id"]
    community2_id = list(community2.hits)[0]["id"]

    # Check that community1 is featured
    community1_featured_entry = service.featured_list(system_identity, community1_id)
    assert community1_featured_entry.total == 1

    # Check that community2 is not featured
    community2_featured_entry = service.featured_list(system_identity, community2_id)
    assert community2_featured_entry.total == 0

    # make sure the right logo was uploaded for community1
    logo = service.read_logo(system_identity, community1_id)
    with logo.open_stream("rb") as fs1, open(
        Path(communities.logo_path) / "community1.png", "rb"
    ) as fs2:
        assert fs1.read() == fs2.read()

    # make sure community2 has no logo
    with pytest.raises(FileNotFoundError):
        service.read_logo(system_identity, community2_id)


def test_load_records(app, db, location, vocabularies):
    dir_ = Path(__file__).parent
    service = current_rdm_records.records_service
    records = RecordsFixture(
        [dir_ / "app_data", dir_.parent.parent / "invenio_rdm_records/fixtures/data"],
        "records.yaml",
        create_demo_record,
        delay=False,
    )

    records.load()

    # Refresh to make changes live
    service.record_cls.index.refresh()

    record1 = service.search(system_identity, q=f"Record1")
    record2 = service.search(system_identity, q=f"Record2")

    assert record1.total == 1
    assert record2.total == 1


def test_load_affiliations(app, db, admin_role, search_clear, affiliations_service):
    dir_ = Path(__file__).parent
    affiliations = VocabularyEntry(
        "affiliations",
        dir_ / "app_data",
        "affiliations",
        {
            "pid-type": "aff",
            "data-file": "vocabularies/affiliations_ror.yaml",
        },
    )

    affiliations.load(system_identity, delay=False)

    cern = affiliations_service.read(identity=system_identity, id_="01ggx4157")
    assert cern["acronym"] == "CERN"

    with pytest.raises(NoResultFound):
        affiliations_service.read(system_identity, "cern")
