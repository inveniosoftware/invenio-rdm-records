# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test version schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import MetadataSchema


@pytest.mark.parametrize("version", [("v1.0.0")])
def test_valid_version(version, app, minimal_record):
    metadata = minimal_record["metadata"]
    metadata["version"] = version
    data = MetadataSchema().load(metadata)
    assert data["version"] == metadata["version"]


@pytest.mark.parametrize("version", [(1), ({"version": "1.0.0"}), (["v1.0.0"])])
def test_invalid_version(version, app, minimal_record):
    metadata = minimal_record["metadata"]
    metadata["version"] = version

    with pytest.raises(ValidationError):
        data = MetadataSchema().load(metadata)
