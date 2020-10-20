# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test metadata publication date schema."""

import pytest
from marshmallow import ValidationError

from invenio_rdm_records.services.schemas import MetadataSchema


def _assert_meta(metadata, value):
    metadata['publication_date'] = value
    data = MetadataSchema().load(metadata)
    assert data['publication_date'] == metadata['publication_date']


def _assert_fails(metadata, value):
    metadata['publication_date'] = value
    with pytest.raises(ValidationError):
        data = MetadataSchema().load(metadata)


# NOTE: The tests need the app ctx because `resource_type` uses the app to
#       access the vocabularies in `validate_entry`.
def test_date(app, minimal_record):
    _assert_meta(minimal_record['metadata'], "2020-12-31")


@pytest.mark.skip("Not supported")
def test_early_date(app, minimal_record):
    _assert_meta(minimal_record['metadata'], "500")


@pytest.mark.skip("Not supported")
def test_bc_date(app, minimal_record):
    _assert_meta(minimal_record['metadata'], "-100")


def test_invalid_date(app, minimal_record):
    _assert_fails(minimal_record['metadata'], "endoftheworld")


def test_year_range(app, minimal_record):
    _assert_meta(minimal_record['metadata'], "2020")


def test_month_range(app, minimal_record):
    _assert_meta(minimal_record['metadata'], "2020-12")


def test_interval(app, minimal_record):
    _assert_meta(minimal_record['metadata'], "2020-01/2020-12")


def test_asymmetric_interval(app, minimal_record):
    _assert_meta(minimal_record['metadata'], "2020-01-01/2020-12")
    _assert_meta(minimal_record['metadata'], "2020-01/2020-12-01")


def test_invalid_interval(app, minimal_record):
    _assert_fails(minimal_record['metadata'], "2021-01/2020-12")
    _assert_fails(minimal_record['metadata'], "/2020-12")
