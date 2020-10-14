# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

import pytest
from invenio_db import db
from invenio_records.dumpers import ElasticsearchDumper

from invenio_rdm_records.records import BibliographicRecord
from invenio_rdm_records.records.dumpers import EDTFDumperExt


@pytest.mark.parametrize("date, expected_start, expected_end", [
    ("2021-01-01", "2021-01-01", "2021-01-01"),
    ("2021-01", "2021-01-01", "2021-01-31"),
    ("2021", "2021-01-01", "2021-12-31"),
    ("1776", "1776-01-01", "1776-12-31"),
    ("2021-01/2021-03", "2021-01-01", "2021-03-31")
])
def test_esdumper_with_edtfext(app, db, minimal_record,
                               date, expected_start, expected_end):
    """Test edft extension implementation."""
    # Create a simple extension that adds a computed field.

    dumper = ElasticsearchDumper(
        extensions=[EDTFDumperExt('metadata.publication_date')])

    minimal_record['metadata']['publication_date'] = date

    # Create the record
    record = BibliographicRecord.create(minimal_record)
    db.session.commit()

    # Dump it
    dump = record.dumps(dumper=dumper)
    assert dump['metadata']['publication_date_start'] == expected_start
    assert dump['metadata']['publication_date_end'] == expected_end
    assert dump['metadata']['publication_date'] == date

    # Load it
    new_record = BibliographicRecord.loads(dump, loader=dumper)
    assert 'publication_date_start' not in new_record['metadata']
    assert 'publication_date_end' not in new_record['metadata']
    assert 'publication_date' in new_record['metadata']


def test_esdumper_with_edtfext_not_defined(app, db, minimal_record):
    """Test edft extension implementation."""
    # Create a simple extension that adds a computed field.

    dumper = ElasticsearchDumper(
        extensions=[EDTFDumperExt('metadata.non_existing_field')])

    # Create the record
    record = BibliographicRecord.create(minimal_record)
    db.session.commit()

    # Dump it
    dump = record.dumps(dumper=dumper)
    assert 'non_existing_field_start' not in dump['metadata']
    assert 'non_existing_field_end' not in dump['metadata']
    assert 'non_existing_field' not in dump['metadata']

    # Load it
    new_record = BibliographicRecord.loads(dump, loader=dumper)
    assert 'non_existing_field_start' not in new_record['metadata']
    assert 'non_existing_field_end' not in new_record['metadata']
    assert 'non_existing_field' not in new_record['metadata']


def test_esdumper_with_edtfext_parse_error(app, db, minimal_record):
    """Test edft extension implementation."""
    # NOTE: We cannot trigger this on publication_date because it is checked
    # by marshmallow on record creation. We can simply give a non date field.
    dumper = ElasticsearchDumper(
        extensions=[EDTFDumperExt('metadata.resource_type.type')])

    # Create the record
    record = BibliographicRecord.create(minimal_record)
    db.session.commit()

    # Dump it
    dump = record.dumps(dumper=dumper)
    assert 'type_start' not in dump['metadata']['resource_type']
    assert 'type_end' not in dump['metadata']['resource_type']
    assert 'type' in dump['metadata']['resource_type']

    # Load it
    new_record = BibliographicRecord.loads(dump, loader=dumper)
    assert 'type_start' not in new_record['metadata']['resource_type']
    assert 'type_end' not in new_record['metadata']['resource_type']
    assert 'type' in new_record['metadata']['resource_type']
