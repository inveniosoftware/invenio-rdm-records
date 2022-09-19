# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test sizes schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import MetadataSchema


@pytest.mark.parametrize("size", [([]), (["100 pages"])])
def test_valid_size(size, app, minimal_record):
    metadata = minimal_record["metadata"]
    metadata["sizes"] = size
    data = MetadataSchema().load(metadata)
    assert data["sizes"] == metadata["sizes"]


@pytest.mark.parametrize("size", [([100]), ("11 pages"), ([""])])
def test_invalid_size(size, app, minimal_record):
    metadata = minimal_record["metadata"]
    metadata["sizes"] = size

    with pytest.raises(ValidationError):
        data = MetadataSchema().load(metadata)
