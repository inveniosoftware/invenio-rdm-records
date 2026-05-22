# SPDX-FileCopyrightText: 2021 Northwestern University.
# SPDX-FileCopyrightText: 2025 California Institute of Technology.
# SPDX-License-Identifier: MIT

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
    expected_messages = [
        "Vocabulary 'resourcetypes' cannot have multiple sources ",
        "'tests.fixtures.load_error.conflicting_module_A.fixtures.vocabularies'",
        "'tests.fixtures.load_error.conflicting_module_B.fixtures.vocabularies'",
        "Vocabulary 'MeSH' cannot have multiple sources ",
    ]
    for line in expected_messages:
        assert any(line in message for message in messages)
