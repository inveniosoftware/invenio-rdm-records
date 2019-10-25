# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University,
#                    Galter Health Sciences Library & Learning Center.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for Invenio RDM Records JSON Schemas."""

from datetime import datetime

import pytest

from invenio_rdm_records.marshmallow.json import MetadataSchemaV1


@pytest.mark.parametrize(('val', 'expected'), [
    (dict(type='publication', subtype='preprint'), None),
    (dict(type='image', subtype='photo'), None),
    (dict(type='dataset'), None),
    (dict(type='dataset', title='Dataset'), dict(type='dataset')),
])
def test_valid_resource_type(val, expected):
    """Test resource type."""
    data, errors = MetadataSchemaV1(partial=['resource_type']).load(
        dict(resource_type=val))
    assert data['resource_type'] == val if expected is None else expected


@pytest.mark.parametrize('val', [
    dict(type='image', subtype='preprint'),
    dict(subtype='photo'),
    dict(type='invalid'),
    dict(title='Dataset'),
    dict(),
])
def test_invalid_resource_type(val):
    """Test resource type."""
    data, errors = MetadataSchemaV1(partial=['resource_type']).load(
        dict(resource_type=val))
    assert 'resource_type' in errors


@pytest.mark.parametrize(('val', 'expected'), [
    ('Test', 'Test',),
    (' Test ', 'Test'),
    ('', None),
    ('  ', None),
])
def test_title(val, expected):
    """Test title."""
    data, errors = MetadataSchemaV1(partial=['title']).load(
        dict(title=val))
    if expected is not None:
        assert data['title'] == expected
    else:
        assert 'title' in errors
        assert 'title' not in data


@pytest.mark.parametrize(('val', 'expected'), [
    ([dict(title='Full additional title',
           title_type='Title type',
           lang='en')], None),
    ([dict(title='Only required field')], None),
])
def test_valid_additional_titles(val, expected):
    """Test additional titles."""
    data, errors = MetadataSchemaV1(partial=['additional_titles']).load(
        dict(additional_titles=val))
    assert data['additional_titles'] == val if expected is None else expected


@pytest.mark.parametrize('val', [
    ([dict(title_type='Invalid title type', lang='en')], None),
])
def test_invalid_additional_titles(val):
    """Test additional titles."""
    data, errors = MetadataSchemaV1(partial=['additional_titles']).load(
        dict(additional_titles=val))
    assert 'additional_titles' in errors


@pytest.mark.parametrize(('val', 'expected'), [
    ('2016-01-02', '2016-01-02'),
    (' 2016-01-02 ', '2016-01-02'),
    ('0001-01-01', '0001-01-01'),
    (None, datetime.utcnow().date().isoformat()),
    ('2016', datetime.utcnow().date().isoformat()),
])
def test_valid_publication_date(val, expected):
    """Test publication date."""
    data, errors = MetadataSchemaV1(partial=['publication_date']).load(
        dict(publication_date=val) if val is not None else dict())
    assert data['publication_date'] == val if expected is None else expected


@pytest.mark.parametrize('val', [
    '2016-02-32',
    ' invalid',
])
def test_invalid_publication_date(val):
    """Test publication date."""
    data, errors = MetadataSchemaV1(partial=['publication_date']).load(
        dict(publication_date=val))
    assert 'publication_date' in errors
    assert 'publication_date' not in data
