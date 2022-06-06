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


def test_valid_full():
    valid_full = {
        "description": "A Romans story",
        "type": {"id": "other"},
        "lang": {"id": "eng"},
    }
    assert valid_full == DescriptionSchema().load(valid_full)


def test_valid_minimal():
    valid_minimal = {"description": "A Romans story", "type": {"id": "other"}}
    assert valid_minimal == DescriptionSchema().load(valid_minimal)


def test_invalid_no_description():
    invalid_no_description = {"type": {"id": "other"}, "lang": {"id": "eng"}}

    assert_raises_messages(
        lambda: DescriptionSchema().load(invalid_no_description),
        {"description": ["Missing data for required field."]},
    )


def test_invalid_description_empty():
    invalid_description_empty = {
        "description": "",
        "type": {"id": "other"},
        "lang": {"id": "eng"},
    }

    assert_raises_messages(
        lambda: DescriptionSchema().load(invalid_description_empty),
        {"description": ["Shorter than minimum length 3."]},
    )


def test_invalid_too_short():
    too_short = {"description": "AA", "type": {"id": "other"}, "lang": {"id": "eng"}}

    assert_raises_messages(
        lambda: DescriptionSchema().load(too_short),
        {"description": ["Shorter than minimum length 3."]},
    )


def test_invalid_description_type():
    invalid_description_type = {
        "description": "A Romans story",
        "type": "Invalid",
        "lang": {"id": "eng"},
    }

    assert_raises_messages(
        lambda: DescriptionSchema().load(invalid_description_type),
        {"type": {"_schema": ["Invalid input type."]}},
    )


@pytest.mark.skip(reason="currently don't know how to test this")
def test_invalid_lang():
    invalid_lang = {
        "description": "A Romans story",
        "type": {"id": "other"},
        "lang": "inv",
    }

    assert_raises_messages(
        lambda: DescriptionSchema().load(invalid_lang),
        {"lang": ["Language must be a lower-cased 3-letter ISO 639-3 string."]},
    )
