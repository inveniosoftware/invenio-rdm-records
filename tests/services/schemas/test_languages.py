# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test languages schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import MetadataSchema


def test_valid_languages(app, minimal_record):
    metadata = minimal_record['metadata']
    metadata['languages'] = ["dan", "eng"]
    data = MetadataSchema().load(metadata)
    assert data['languages'] == metadata['languages']


def test_invalid_iso_3_languages(app, minimal_record):
    metadata = minimal_record['metadata']
    metadata['languages'] = ["da"]

    with pytest.raises(ValidationError):
        data = MetadataSchema().load(metadata)


def test_invalid_no_list_languages(app, minimal_record):
    metadata = minimal_record['metadata']
    metadata['languages'] = "eng"

    with pytest.raises(ValidationError):
        data = MetadataSchema().load(metadata)


def test_invalid_code_languages(app, minimal_record):
    metadata = minimal_record['metadata']
    metadata['languages'] = ["inv"]

    with pytest.raises(ValidationError):
        data = MetadataSchema().load(metadata)
