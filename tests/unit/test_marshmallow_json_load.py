# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University,
#                    Galter Health Sciences Library & Learning Center.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Tests for Invenio RDM Records JSON Schemas."""

from datetime import date, datetime

import pytest

from invenio_rdm_records.marshmallow.json import InternalSchemaV1, \
    MetadataSchemaV1


@pytest.mark.parametrize(('value',), [
    (dict(type='publication', subtype='preprint'),),
    (dict(type='image', subtype='photo'),),
    (dict(type='dataset'),),
])
def test_valid_resource_type(value):
    """Test resource type."""
    data, errors = (
        MetadataSchemaV1(partial=True).load(dict(resource_type=value))
    )

    assert data['resource_type'] == value
    assert not errors


@pytest.mark.parametrize('value', [
    dict(type='image', subtype='preprint'),
    dict(type='dataset', title='Dataset'),
    dict(subtype='photo'),
    dict(type='invalid'),
    dict(title='Dataset'),
    dict(),
])
def test_invalid_resource_type(value):
    """Test resource type."""
    data, errors = (
        MetadataSchemaV1(partial=True).load(dict(resource_type=value))
    )

    assert 'resource_type' in errors


@pytest.mark.parametrize(('value', 'expected'), [
    ('Test', 'Test',),
    (' Test ', 'Test'),
    ('', None),
    ('  ', None),
])
def test_title(value, expected):
    """Test title."""
    data, errors = MetadataSchemaV1(partial=True).load(dict(title=value))
    if expected is not None:
        assert data['title'] == expected
    else:
        assert 'title' in errors
        assert 'title' not in data


@pytest.mark.parametrize(('value', 'expected'), [
    ([dict(title='Full additional title',
           title_type='Other',
           lang='eng')], None),
    ([dict(title='Only required field')], None),
])
def test_valid_additional_titles(value, expected):
    """Test additional titles."""
    data, errors = MetadataSchemaV1(partial=True).load(
        dict(additional_titles=value))
    assert data['additional_titles'] == value if expected is None else expected
    assert not errors


@pytest.mark.parametrize('value', [
    ([dict(title_type='Invalid title type', lang='eng')], None),
    ([dict(title_type='Other', lang='eng')], None),
    ([dict(title='Invalid lang', title_type='Other', lang='en')], None),
])
def test_invalid_additional_titles(value):
    """Test additional titles."""
    data, errors = MetadataSchemaV1(partial=True).load(
        dict(additional_titles=value))
    assert 'additional_titles' in errors


@pytest.mark.parametrize(('value', 'expected'), [
    ([dict(description='Full additional description',
           description_type='Other',
           lang='eng')], None),
    ([dict(description='Only required fields',
           description_type='Other')], None),
])
def test_valid_additional_descriptions(value, expected):
    """Test additional descriptions."""
    data, errors = MetadataSchemaV1(partial=True).load(
        dict(additional_descriptions=value))

    if expected is not None:
        assert data['additional_descriptions'] == expected
    else:
        assert data['additional_descriptions'] == value

    assert not errors


@pytest.mark.parametrize('value', [
    ([dict(description_type='Other', lang='eng')], None),
    ([dict(description='Invalid no description type', lang='eng')], None),
    ([dict(lang='eng')], None),
    ([dict(description='Invalid type',
           description_type='Invalid Type', lang='eng')], None),
    ([dict(description='Invalid lang',
           description_type='Other', lang='en')], None),
])
def test_invalid_additional_descriptions(value):
    """Test additional descriptions."""
    data, errors = MetadataSchemaV1(partial=True).load(
        dict(additional_descriptions=value))
    assert 'additional_descriptions' in errors


@pytest.mark.parametrize(('value', 'expected'), [
    ('2016-01-02', '2016-01-02'),
    (' 2016-01-02 ', '2016-01-02'),
    ('0001-01-01', '0001-01-01'),
    (None, datetime.utcnow().date().isoformat()),
    ('2016', datetime.utcnow().date().isoformat()),
])
def test_valid_publication_date(value, expected):
    """Test publication date."""
    data, errors = MetadataSchemaV1(partial=True).load(
        dict(publication_date=value) if value is not None else dict())
    assert data['publication_date'] == value if expected is None else expected
    assert not errors


@pytest.mark.parametrize('value', [
    '2016-02-32',
    ' invalid',
])
def test_invalid_publication_date(value):
    """Test publication date."""
    data, errors = MetadataSchemaV1(partial=True).load(
        dict(publication_date=value))
    assert 'publication_date' in errors
    assert 'publication_date' not in data


@pytest.mark.parametrize(('value', 'expected'), [
    ('2116-01-02', '2116-01-02'),
    (' 2116-01-02 ', '2116-01-02'),
    ('2116-01', '2116-01-{0:2d}'.format(date.today().day)),
    ('2116', '2116-{:2d}-{:2d}'.format(
        date.today().month, date.today().day
    )),
    ('2016-01-02', None),
    (None, None),
    ({}, None),
])
def test_embargo_date(value, expected):
    data, errors = MetadataSchemaV1(partial=True).load(
        dict(embargo_date=value)
    )

    if expected:
        assert data['embargo_date'] == expected
        assert not errors
    else:
        assert 'embargo_date' in errors


def test_dates():
    """Test dates."""
    schema = MetadataSchemaV1(partial=True)

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
    msv1 = MetadataSchemaV1(partial=True)
    data, errors = msv1.load(dict(language='eng'))
    assert data['language'] == 'eng'
    assert 'language' not in errors
    data, errors = msv1.load(dict(language='English'))
    assert 'language' in errors
    data, errors = msv1.load(dict())
    assert 'language' not in errors


@pytest.mark.parametrize(('value', 'expected'), [
    ([dict(rights='Full rights schema',
           uri='http://creativecommons.org/l',
           identifier='CC-BY-3.0',
           identifier_scheme='SPDX',
           scheme_uri='https://spdx.org/licenses',
           lang='eng')], None),
    ([dict(rights='Random rights with only free text')], None),
    ([dict()], None)
])
def test_valid_rights(value, expected):
    """Test rights."""
    data, errors = MetadataSchemaV1(partial=True).load(
        dict(rights=value))

    assert data['rights'] == value if expected is None else expected

    data, errors = MetadataSchemaV1(partial=True).load(
        {'rights': [{'lang': 'en'}]}
    )
    assert 'lang' not in errors


@pytest.mark.parametrize(('access_right', 'valid'), [
    ('open', True),
    ('embargoed', True),
    ('restricted', True),
    ('closed', True),
    ('FOO', False)
])
def test_access_right(access_right, valid):
    data, errors = (
        MetadataSchemaV1(partial=True).load({'access_right': access_right})
    )

    if valid:
        assert not errors
        assert data['access_right'] == access_right
    else:
        assert 'access_right' in errors


def test_sys_schema():
    sys = {'permissions': {}}

    data, errors = MetadataSchemaV1(partial=True).load({'sys': sys})

    assert not errors
    assert data['sys'] == sys


def test_permissions():
    input_permissions = {
        'permissions': {
            'can_read': [{'id': '1', 'type': 'person'}],
            'can_foo': [{'id': '2', 'type': 'org'}],
            'bar': 'baz'
        }
    }

    # Happy path
    data, errors = InternalSchemaV1(partial=True).load(input_permissions)

    assert not errors
    # InternalSchemaV1 silently nixes non can_<action> field
    assert data['permissions'] == {
        'can_read': [{'id': '1', 'type': 'person'}],
        'can_foo': [{'id': '2', 'type': 'org'}]
    }

    # error cases
    cases = [{'id': '1'}, {'type': 'person'}, {'id': '1', 'type': 'baz'}]
    for case in cases:
        input_permissions['permissions']['can_foo'] = [case]

        data, errors = InternalSchemaV1(partial=True).load(input_permissions)

        assert errors
        assert 'permissions' in errors
