# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
from pathlib import Path

import pytest
from invenio_access.permissions import system_identity

from invenio_rdm_records.fixtures.vocabularies import (
    ConflictingFixturesError,
    PrioritizedVocabulariesFixtures,
)


def test_conflicting_load(app):
    dir_ = Path(__file__).parent.parent
    vocabularies = PrioritizedVocabulariesFixtures(
        system_identity, dir_ / "app_data", dir_ / "data"
    )

    with pytest.raises(ConflictingFixturesError) as e:
        vocabularies.load()

    messages = e.value.errors
    expected_messages = set(
        [
            "Vocabulary 'resourcetypes' cannot have multiple sources "
            "['conflicting_module_A.fixtures.vocabularies', "
            "'conflicting_module_B.fixtures.vocabularies']",
            "Vocabulary 'MeSH' cannot have multiple sources "
            "['conflicting_module_A.fixtures.vocabularies', "
            "'conflicting_module_B.fixtures.vocabularies']",
        ]
    )
    assert expected_messages == set(messages)
