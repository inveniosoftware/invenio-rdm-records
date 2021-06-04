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


def test_valid_subject():
    valid_full = {
        "id": "A-D000007",
    }

    assert valid_full == SubjectSchema().load(valid_full)


def test_invalid_subject():
    invalid_no_subject = {
        "identifier": "A-D000007"
    }

    with pytest.raises(ValidationError):
        SubjectSchema().load(invalid_no_subject)

    # 'title' is dump_only, passing it in is invalid
    invalid_title = {
        "title": "Abdominal Injuries"
    }

    with pytest.raises(ValidationError):
        SubjectSchema().load(invalid_title)
