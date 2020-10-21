# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test subjects schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import SubjectSchema


def test_valid_subject():
    valid_full = {
        "subject": "Romans",
        "identifier": "subj-1",
        "scheme": "no-scheme"
    }

    assert valid_full == SubjectSchema().load(valid_full)


def test_valid_minimal_subject():
    valid_minimal = {
        "subject": "Romans"
    }

    assert valid_minimal == SubjectSchema().load(valid_minimal)


def test_invalid_subject():
    invalid_no_subject = {
        "identifier": "subj-1",
        "scheme": "no-scheme"
    }

    with pytest.raises(ValidationError):
        data = SubjectSchema().load(invalid_no_subject)
