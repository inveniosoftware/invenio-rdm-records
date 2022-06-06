# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test formats schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import MetadataSchema


@pytest.mark.parametrize("format", [([]), (["application/pdf"])])
def test_valid_size(format, app, minimal_record):
    metadata = minimal_record["metadata"]
    metadata["formats"] = format
    data = MetadataSchema().load(metadata)
    assert data["formats"] == metadata["formats"]


@pytest.mark.parametrize("format", [([100]), ("jpeg"), ([""])])
def test_invalid_size(format, app, minimal_record):
    metadata = minimal_record["metadata"]
    metadata["formats"] = format

    with pytest.raises(ValidationError):
        data = MetadataSchema().load(metadata)
