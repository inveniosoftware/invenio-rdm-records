# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-FileCopyrightText: 2021 Northwestern University.
# SPDX-License-Identifier: MIT

"""Test languages schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import MetadataSchema


def test_valid_languages(app, minimal_record):
    metadata = minimal_record["metadata"]
    metadata["languages"] = [{"id": "dan"}, {"id": "eng"}]
    data = MetadataSchema().load(metadata)
    assert data["languages"] == metadata["languages"]


def test_invalid_no_list_languages(app, minimal_record):
    metadata = minimal_record["metadata"]
    metadata["languages"] = {"id": "eng"}

    with pytest.raises(ValidationError):
        data = MetadataSchema().load(metadata)
