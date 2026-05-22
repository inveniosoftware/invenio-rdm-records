# SPDX-FileCopyrightText: 2019-2021 CERN.
# SPDX-FileCopyrightText: 2019-2021 Northwestern University.
# SPDX-License-Identifier: MIT

"""Tests for Invenio RDM Records MetadataSchema."""

import pytest
from marshmallow import ValidationError
from marshmallow.fields import Bool, Integer, List
from marshmallow_utils.fields import ISODateString, SanitizedUnicode

from invenio_rdm_records.services.schemas.metadata import MetadataSchema


def test_full_metadata_schema(app, full_metadata):
    """Test metadata schema."""
    # Test full attributes

    data = MetadataSchema().load(full_metadata)
    assert data == full_metadata


def test_minimal_metadata_schema(app, minimal_metadata, expected_minimal_metadata):
    metadata = MetadataSchema().load(minimal_metadata)

    assert expected_minimal_metadata == metadata


def test_additional_field_raises(app, minimal_metadata):
    minimal_metadata["foo"] = "FOO"

    with pytest.raises(ValidationError):
        MetadataSchema().load(minimal_metadata)
