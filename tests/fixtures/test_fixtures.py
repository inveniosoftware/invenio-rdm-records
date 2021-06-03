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
from invenio_vocabularies.proxies import current_service as vocabulary_service

from invenio_rdm_records.fixtures.users import UsersFixture
from invenio_rdm_records.fixtures.vocabularies import VocabulariesFixture


def test_load_languages(app, db, vocabularies):
    vocabularies.load_vocabulary(
        'languages',
        {
            "pid-type": "lng",
            "data-file": (
                Path(__file__).parent / "data/vocabularies/languages.yaml"
            )
        },
        delay=False
    )

    item = vocabulary_service.read(
        ('languages', 'aae'), system_identity)

    assert item.id == "aae"


def test_load_resource_types(app, db, vocabularies):
    vocabularies.load_vocabulary(
        'resource_types',
        {
            "pid-type": "rsrct",
            "data-file": (
                Path(__file__).parent / "data/vocabularies/resource_types.yaml"
            )
        },
        delay=False
    )

    item = vocabulary_service.read(
        ('resource_types', 'publication-annotationcollection'),
        system_identity
    )
    item_dict = item.to_dict()

    assert item_dict["id"] == "publication-annotationcollection"
    assert item_dict["props"]["datacite_general"] == "Collection"


def test_loading_paths_traversal(app, db):
    dir_ = Path(__file__).parent
    vocabularies = VocabulariesFixture(
        system_identity,
        [dir_ / "app_data", dir_ / "data"],
        "vocabularies.yaml"
    )

    vocabularies.load()

    # app_data/vocabularies/resource_types.yaml only has image resource types
    with pytest.raises(PIDDoesNotExistError):
        vocabulary_service.read(
            ('resource_types', 'publication-annotationcollection'),
            system_identity
        )

    # languages are found
    item = vocabulary_service.read(('languages', 'aae'), system_identity)
    assert item.id == "aae"

    # subjects A from app_data/ are loaded
    item = vocabulary_service.read(('subjects', 'A-D000008'), system_identity)
    assert item.id == "A-D000008"


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
