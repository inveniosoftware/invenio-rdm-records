# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test metadata titles schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import TitleSchema

from .test_utils import assert_raises_messages


def test_valid_full():
    valid_full = {
        "title": "A Romans story",
        "type": {"id": "other"},
        "lang": {"id": "eng"},
    }
    assert valid_full == TitleSchema().load(valid_full)


def test_valid_minimal():
    valid_partial = {
        "title": "A Romans story",
        "type": {"id": "other"},
    }
    assert valid_partial == TitleSchema().load(valid_partial)


def test_invalid_no_type():
    invalid_no_type = {"title": "A Romans story", "lang": {"id": "eng"}}

    assert_raises_messages(
        lambda: TitleSchema().load(invalid_no_type),
        {"type": ["Missing data for required field."]},
    )


def test_invalid_no_title():
    invalid_no_title = {"type": {"id": "other"}, "lang": {"id": "eng"}}

    assert_raises_messages(
        lambda: TitleSchema().load(invalid_no_title),
        {"title": ["Missing data for required field."]},
    )


def test_invalid_title_empty():
    invalid_title_empty = {"title": "", "type": {"id": "other"}, "lang": {"id": "eng"}}

    assert_raises_messages(
        lambda: TitleSchema().load(invalid_title_empty),
        {"title": ["Shorter than minimum length 3."]},
    )


def test_invalid_too_short():
    too_short = {"title": "AA", "type": {"id": "other"}, "lang": {"id": "eng"}}

    assert_raises_messages(
        lambda: TitleSchema().load(too_short),
        {"title": ["Shorter than minimum length 3."]},
    )


@pytest.mark.skip(reason="currently don't know how to test this")
def test_invalid_title_type():
    invalid_title_type = {
        "title": "A Romans story",
        "type": {"id": "Invalid"},
        "lang": {"id": "eng"},
    }

    with pytest.raises(ValidationError):
        TitleSchema().load(invalid_title_type)


@pytest.mark.skip(reason="currently don't know how to test this")
def test_invalid_lang():
    invalid_lang = {
        "title": "A Romans story",
        "type": {"id": "other"},
        "lang": {"id": "inv"},
    }

    assert_raises_messages(
        lambda: TitleSchema().load(invalid_lang),
        {"lang": ["Language must be a lower-cased 3-letter ISO 639-3 string."]},
    )
