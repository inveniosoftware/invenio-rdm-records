# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test metadata descriptions schema."""

import pytest
from flask_babelex import lazy_gettext as _
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import DescriptionSchema

from .test_utils import assert_raises_messages


def test_valid_full(vocabulary_clear):
    valid_full = {
        "description": "A Romans story",
        "type": "other",
        "lang": {
            "id": "eng"
        }
    }
    assert valid_full == DescriptionSchema().load(valid_full)


def test_valid_minimal(vocabulary_clear):
    valid_minimal = {
        "description": "A Romans story",
        "type": "other"
    }
    assert valid_minimal == DescriptionSchema().load(valid_minimal)


def test_invalid_no_description(vocabulary_clear):
    invalid_no_description = {
        "type": "other",
        "lang": {
            "id": "eng"
        }
    }

    assert_raises_messages(
        lambda: DescriptionSchema().load(invalid_no_description),
        {'description': ['Missing data for required field.']}
    )


def test_invalid_description_empty(vocabulary_clear):
    invalid_description_empty = {
        "description": "",
        "type": "other",
        "lang": {
            "id": "eng"
        }
    }

    assert_raises_messages(
        lambda: DescriptionSchema().load(invalid_description_empty),
        {'description': ['Shorter than minimum length 3.']}
    )


def test_invalid_too_short(vocabulary_clear):
    too_short = {
        "description": "AA",
        "type": "other",
        "lang": {
            "id": "eng"
        }
    }

    assert_raises_messages(
        lambda: DescriptionSchema().load(too_short),
        {'description': ['Shorter than minimum length 3.']}
    )


def test_invalid_description_type(vocabulary_clear):
    invalid_description_type = {
        "description": "A Romans story",
        "type": "Invalid",
        "lang": {
            "id": "eng"
        }
    }

    assert_raises_messages(
        lambda: DescriptionSchema().load(invalid_description_type),
        {'type': [_(
            "Invalid description type. Invalid not one of abstract, " +
            "methods, seriesinformation, tableofcontents, technicalinfo, " +
            "other."
        )]}
    )


@pytest.mark.skip(reason="currently don't know how to test this")
def test_invalid_lang(vocabulary_clear):
    invalid_lang = {
        "description": "A Romans story",
        "type": "other",
        "lang": "inv"
    }

    assert_raises_messages(
        lambda: DescriptionSchema().load(invalid_lang),
        {'lang': ['Language must be a lower-cased 3-letter ISO 639-3 string.']}
    )
