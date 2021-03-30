# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

import pytest
from flask_principal import Identity, UserNeed
from flask_security import login_user
from invenio_access.permissions import SystemRoleNeed
from invenio_records.dumpers import ElasticsearchDumper

from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.records import RDMDraft, RDMRecord
from invenio_rdm_records.records.api import RDMParent
from invenio_rdm_records.records.dumpers import EDTFDumperExt, \
    EDTFListDumperExt


@pytest.mark.parametrize("date, expected_start, expected_end", [
    ("2021-01-01", "2021-01-01", "2021-01-01"),
    ("2021-01", "2021-01-01", "2021-01-31"),
    ("2021", "2021-01-01", "2021-12-31"),
    ("1776", "1776-01-01", "1776-12-31"),
    ("2021-01/2021-03", "2021-01-01", "2021-03-31")
])
def test_esdumper_with_edtfext(app, db, minimal_record, location,
                               date, expected_start, expected_end):
    """Test edft extension implementation."""
    # Create a simple extension that adds a computed field.

    dumper = ElasticsearchDumper(
        extensions=[
            EDTFDumperExt("metadata.publication_date"),
            EDTFListDumperExt("metadata.dates", "date"),
        ]
    )

    minimal_record["metadata"]["publication_date"] = date
    minimal_record["metadata"]["dates"] = [{"date": date}]

    # Create the record
    record = RDMRecord.create(minimal_record, parent=RDMParent.create({}))
    db.session.commit()

    # Dump it
    dump = record.dumps(dumper=dumper)
    assert dump["metadata"]["publication_date_range"]["gte"] == expected_start
    assert dump["metadata"]["publication_date_range"]["lte"] == expected_end
    assert dump["metadata"]["publication_date"] == date
    assert dump["metadata"]["dates"][0]["date_range"]["gte"] == expected_start
    assert dump["metadata"]["dates"][0]["date_range"]["lte"] == expected_end
    assert dump["metadata"]["dates"][0]["date"] == date

    # Load it
    new_record = RDMRecord.loads(dump, loader=dumper)
    assert "publication_date_range" not in new_record["metadata"]
    assert "publication_date" in new_record["metadata"]
    assert "date_range" not in new_record["metadata"]["dates"][0]
    assert "date" in new_record["metadata"]["dates"][0]


def test_esdumper_with_edtfext_not_defined(app, db, location, minimal_record):
    """Test edft extension implementation."""
    # Create a simple extension that adds a computed field.

    dumper = ElasticsearchDumper(
        extensions=[
            EDTFDumperExt("metadata.non_existing_field"),
        ]
    )

    # Create the record
    record = RDMRecord.create(minimal_record, parent=RDMParent.create({}))
    db.session.commit()

    # Dump it
    dump = record.dumps(dumper=dumper)
    assert "non_existing_field_range" not in dump["metadata"]
    assert "non_existing_field" not in dump["metadata"]

    # Load it
    new_record = RDMRecord.loads(dump, loader=dumper)
    assert "non_existing_field_range" not in new_record["metadata"]
    assert "non_existing_field" not in new_record["metadata"]


def test_eslistdumper_with_edtfext_not_defined(app, db, minimal_record):
    """Test edft extension implementation."""
    # Create a simple extension that adds a computed field.

    dumper = ElasticsearchDumper(
        extensions=[
            EDTFListDumperExt("metadata.non_existing_array_field", "date"),
        ]
    )

    # Create the record
    record = RDMRecord.create(minimal_record, parent=RDMParent.create({}))
    db.session.commit()

    # Dump it
    dump = record.dumps(dumper=dumper)
    assert "non_existing_array_field_range" not in dump["metadata"]
    assert "non_existing_array_field" not in dump["metadata"]

    # Load it
    new_record = RDMRecord.loads(dump, loader=dumper)
    assert "non_existing_array_field_range" not in new_record["metadata"]
    assert "non_existing_array_field" not in new_record["metadata"]


def test_esdumper_with_edtfext_parse_error(app, db, location, minimal_record):
    """Test edft extension implementation."""
    # NOTE: We cannot trigger this on publication_date because it is checked
    # by marshmallow on record creation. We can simply give a non date field.
    dumper = ElasticsearchDumper(
        extensions=[
            EDTFDumperExt("metadata.resource_type.type"),
        ]
    )

    # Create the record
    record = RDMRecord.create(minimal_record, parent=RDMParent.create({}))
    db.session.commit()

    # Dump it
    dump = record.dumps(dumper=dumper)
    assert "type_range" not in dump["metadata"]["resource_type"]
    assert "type" in dump["metadata"]["resource_type"]

    # Load it
    new_record = RDMRecord.loads(dump, loader=dumper)
    assert "type_range" not in new_record["metadata"]["resource_type"]
    assert "type" in new_record["metadata"]["resource_type"]


def test_eslistdumper_with_edtfext_parse_error(app, db, minimal_record):
    """Test edft extension implementation."""
    dumper = ElasticsearchDumper(
        extensions=[
            EDTFListDumperExt("metadata.creators", "family_name"),
        ]
    )

    # Create the record
    record = RDMRecord.create(minimal_record, parent=RDMParent.create({}))
    db.session.commit()

    # Dump it
    dump = record.dumps(dumper=dumper)
    person_or_org = dump["metadata"]["creators"][0]["person_or_org"]
    assert "family_name_range" not in person_or_org
    assert "family_name" in person_or_org

    # Load it
    new_record = RDMRecord.loads(dump, loader=dumper)
    person_or_org = dump["metadata"]["creators"][0]["person_or_org"]
    assert 'family_name_range' not in person_or_org
    assert 'family_name' in person_or_org
    assert 'type_start' not in new_record['metadata']['resource_type']
    assert 'type_end' not in new_record['metadata']['resource_type']
    assert 'type' in new_record['metadata']['resource_type']
