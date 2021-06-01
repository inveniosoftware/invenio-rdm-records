# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test metadata titles schema."""

import pytest
from flask_babelex import lazy_gettext as _
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas.metadata import TitleSchema

from .test_utils import assert_raises_messages


def test_valid_full(vocabulary_clear):
    valid_full = {
        "title": "A Romans story",
        "type": "other",
        "lang": {
            "id": "eng"
        }
    }
    assert valid_full == TitleSchema().load(valid_full)


def test_valid_partial(vocabulary_clear):
    valid_partial = {
        "title": "A Romans story",
        "lang": {
            "id": "eng"
        }
    }
    assert valid_partial == TitleSchema().load(valid_partial)


def test_valid_minimal(vocabulary_clear):
    valid_minimal = {
        "title": "A Romans story"
    }
    assert valid_minimal == TitleSchema().load(valid_minimal)


def test_invalid_no_title(vocabulary_clear):
    invalid_no_title = {
        "type": "other",
        "lang": {
            "id": "eng"
        }
    }

    assert_raises_messages(
        lambda: TitleSchema().load(invalid_no_title),
        {'title': ['Missing data for required field.']}
    )


def test_invalid_title_empty(vocabulary_clear):
    invalid_title_empty = {
        "title": "",
        "type": "other",
        "lang": {
            "id": "eng"
        }
    }

    assert_raises_messages(
        lambda: TitleSchema().load(invalid_title_empty),
        {'title': ['Shorter than minimum length 3.']}
    )


def test_invalid_too_short(vocabulary_clear):
    too_short = {
        "title": "AA",
        "type": "other",
        "lang": {
            "id": "eng"
        }
    }

    assert_raises_messages(
        lambda: TitleSchema().load(too_short),
        {'title': ['Shorter than minimum length 3.']}
    )


def test_invalid_title_type(vocabulary_clear):
    invalid_title_type = {
        "title": "A Romans story",
        "type": "Invalid",
        "lang": {
            "id": "eng"
        }
    }

    assert_raises_messages(
        lambda: TitleSchema().load(invalid_title_type),
        {'type': [_(
            "Invalid value. Choose one of ['alternativetitle', "
            "'other', 'subtitle', 'translatedtitle']."
        )]}
    )


@pytest.mark.skip(reason="currently don't know how to test this")
def test_invalid_lang(vocabulary_clear):
    invalid_lang = {
        "title": "A Romans story",
        "type": "other",
        "lang": {
            "id": "inv"
        }
    }

    assert_raises_messages(
        lambda: TitleSchema().load(invalid_lang),
        {'lang': ['Language must be a lower-cased 3-letter ISO 639-3 string.']}
    )
