# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
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
    PrioritizedVocabulariesFixtures


def test_load_languages(app, db, vocabularies):
    id_ = 'languages'
    filepath = Path(__file__).parent / "data/vocabularies/languages.yaml"

    vocabularies.create_vocabulary_type(
        id_,
        {
            "pid-type": "lng",
            "data-file": filepath
        },
    )
    vocabularies.load_datafile(id_, filepath, delay=False)

    item = vocabulary_service.read((id_, 'aae'), system_identity)
    assert item.id == "aae"


def test_load_resource_types(app, db, vocabularies):
    id_ = 'resourcetypes'
    filepath = Path(__file__).parent / "data/vocabularies/resource_types.yaml"

    vocabularies.create_vocabulary_type(
        id_,
        {
            "pid-type": "rsrct",
            "data-file": filepath
        },
    )
    vocabularies.load_datafile(id_, filepath, delay=False)

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
