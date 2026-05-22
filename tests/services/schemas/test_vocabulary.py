# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-FileCopyrightText: 2021 Northwestern University.
# SPDX-License-Identifier: MIT

"""Test subjects schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import VocabularySchema


def test_valid_vocabulary():
    valid_full = {
        "id": "A-D000007",
    }

    assert valid_full == VocabularySchema().load(valid_full)


def test_invalid_vocabulary():
    invalid_no_vocabulary = {"identifier": "A-D000007"}

    with pytest.raises(ValidationError):
        VocabularySchema().load(invalid_no_vocabulary)

    # 'title' is dump_only, passing it in is invalid
    invalid_title = {"title": "Abdominal Injuries"}

    with pytest.raises(ValidationError):
        VocabularySchema().load(invalid_title)
