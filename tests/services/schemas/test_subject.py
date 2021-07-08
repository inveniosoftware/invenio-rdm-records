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

from invenio_rdm_records.services.schemas.metadata import SubjectSchema


def test_valid_id():
    valid_id = {
        "id": "test",
    }
    assert valid_id == SubjectSchema().load(valid_id)


def test_valid_subject():
    valid_subject = {
        "subject": "Entity One"
    }
    assert valid_subject == SubjectSchema().load(valid_subject)


def test_valid_full():
    valid_subject = {
        "id": "test",
        "subject": "Entity One",
        "scheme": "MeSH"
    }
    assert valid_subject == SubjectSchema().load(valid_subject)


def test_invalid_empty():
    invalid_empty = {}
    with pytest.raises(ValidationError):
        data = SubjectSchema().load(invalid_empty)
