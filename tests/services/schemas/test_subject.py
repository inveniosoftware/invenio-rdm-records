# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test subjects schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import MetadataSchema


def test_valid_subjects(app, minimal_record):
    metadata = minimal_record['metadata']
    metadata['subjects'] = [{"id": "A-D000007"}, {"id": "A-D000008"}]
    data = MetadataSchema().load(metadata)
    assert data['subjects'] == metadata['subjects']


def test_invalid_no_list_subjects(app, minimal_record):
    metadata = minimal_record['metadata']
    metadata['subjects'] = {"id": "A-D000007"}

    with pytest.raises(ValidationError):
        data = MetadataSchema().load(metadata)
