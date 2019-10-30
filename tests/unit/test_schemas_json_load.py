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
           title_type='Other',
           lang='eng')], None),
    ([dict(title='Only required field')], None),
])
def test_valid_additional_titles(val, expected):
    """Test additional titles."""
    data, errors = MetadataSchemaV1(partial=['additional_titles']).load(
        dict(additional_titles=val))
    assert data['additional_titles'] == val if expected is None else expected


@pytest.mark.parametrize('val', [
    ([dict(title_type='Invalid title type', lang='eng')], None),
    ([dict(title_type='Other', lang='eng')], None),
    ([dict(title='Invalid lang', title_type='Other', lang='en')], None),
])
def test_invalid_additional_titles(val):
    """Test additional titles."""
    data, errors = MetadataSchemaV1(partial=['additional_titles']).load(
        dict(additional_titles=val))
    assert 'additional_titles' in errors


@pytest.mark.parametrize(('val', 'expected'), [
    ([dict(description='Full additional description',
           description_type='Other',
           lang='eng')], None),
    ([dict(description='Only required fields',
           description_type='Other')], None),
])
def test_valid_additional_descriptions(val, expected):
    """Test additional descriptions."""
    data, errors = MetadataSchemaV1(partial=['additional_descriptions']).load(
        dict(additional_descriptions=val))

    if expected is not None:
        assert data['additional_descriptions'] == expected
    else:
        assert data['additional_descriptions'] == val


@pytest.mark.parametrize('val', [
    ([dict(description_type='Other', lang='eng')], None),
    ([dict(description='Invalid no description type', lang='eng')], None),
    ([dict(lang='eng')], None),
    ([dict(description='Invalid type',
           description_type='Invalid Type', lang='eng')], None),
    ([dict(description='Invalid lang',
           description_type='Other', lang='en')], None),
])
def test_invalid_additional_descriptions(val):
    """Test additional descriptions."""
    data, errors = MetadataSchemaV1(partial=['additional_descriptions']).load(
        dict(additional_descriptions=val))
    assert 'additional_descriptions' in errors


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


@pytest.mark.parametrize(('val', 'expected'), [
    ('2016-01-02', '2016-01-02'),
    (' 2016-01-02 ', '2016-01-02'),
    ('0001-01-01', '0001-01-01'),
    (None, datetime.utcnow().date().isoformat()),
    ('2016', datetime.utcnow().date().isoformat()),
])
def test_valid_embargo_date(val, expected):
    """Test embargo date."""
    data, errors = MetadataSchemaV1(partial=['embargo_date']).load(
        dict(embargo_date=val) if val is not None else dict())
    assert data['embargo_date'] == val if expected is None else expected


def test_dates():
    """Test dates."""
    schema = MetadataSchemaV1(partial=['dates'])

    data, errors = schema.load({'dates': None})
    assert 'not be null' in errors['dates'][0]
    data, errors = schema.load({'dates': []})
    assert 'Shorter than minimum' in errors['dates'][0]
    data, errors = schema.load({'dates': [{}]})
    assert 'required field' in errors['dates'][0]['type'][0]
    data, errors = schema.load({'dates': [{'type': 'Valid'}]})
    assert 'at least one date' in errors['dates'][0]
    data, errors = schema.load({'dates': [{'type': 'Valid', 'start': None}]})
    assert 'not be null' in errors['dates'][0]['start'][0]
    data, errors = schema.load({'dates': [{'type': 'Valid', 'start': ''}]})
    assert 'Not a valid date' in errors['dates'][0]['start'][0]
    data, errors = schema.load(
        {'dates': [{'type': 'Invalid',
                    'start': '2019-01-01', 'end': '2019-01-31',
                    'description': 'Some description'}]})
    assert 'Invalid date type' in errors['dates'][0]['type'][0]

    # "start" date after "end"
    data, errors = schema.load(
        {'dates': [{'type': 'Valid',
                    'start': '2019-02-01', 'end': '2019-01-01'}]})
    assert 'must be before "end"' in errors['dates'][0]

    # Single date value (i.e. start == end)
    data, errors = schema.load(
        {'dates': [{'type': 'Valid',
                    'start': '2019-01-01', 'end': '2019-01-01'}]})
    assert 'dates' not in errors
    data, errors = schema.load(
        {'dates': [{'type': 'Valid', 'start': '2019-01-01'}]})
    assert 'dates' not in errors
    data, errors = schema.load(
        {'dates': [{'type': 'Valid', 'end': '2019-01-01'}]})
    assert 'dates' not in errors
    data, errors = schema.load(
        {'dates': [{'type': 'Valid',
                    'start': '2019-01-01', 'end': '2019-01-31',
                    'description': 'Some description'}]})
    assert 'dates' not in errors


def test_language():
    """Test language."""
    msv1 = MetadataSchemaV1(partial=['language'])
    data, errors = msv1.load(dict(language='eng'))
    assert data['language'] == 'eng'
    assert 'language' not in errors
    data, errors = msv1.load(dict(language='English'))
    assert 'language' in errors
    data, errors = msv1.load(dict())
    assert 'language' not in errors


@pytest.mark.parametrize(('val', 'expected'), [
    ([dict(rights='Full rights schema',
           uri='http://creativecommons.org/l',
           identifier='CC-BY-3.0',
           identifier_scheme='SPDX',
           scheme_uri='https://spdx.org/licenses',
           lang='eng')], None),
    ([dict(rights='Random rights with only free text')], None),
    ([dict()], None)
])
def test_valid_rights(val, expected):
    """Test rights."""
    data, errors = MetadataSchemaV1(partial=['rights']).load(
        dict(rights=val))

    assert data['rights'] == val if expected is None else expected

    data, errors = MetadataSchemaV1(partial=['rights']).load(
        {'rights': [{'lang': 'en'}]}
    )
    assert 'lang' not in errors
