# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""
import unittest.mock

import pytest
from invenio_db import db
from invenio_records.dumpers import ElasticsearchDumper

from invenio_rdm_records.records import BibliographicRecord
from invenio_rdm_records.records.dumpers import EDTFDumperExt, LocationsDumper


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


def test_esdumper_with_edtfext_not_defined(app, db, location, minimal_record):
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


def test_esdumper_with_edtfext_parse_error(app, db, location, minimal_record):
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


def test_locationsdumper_with_point_geometry(app, db, minimal_record):
    dumper = ElasticsearchDumper(
        extensions=[LocationsDumper()]
    )

    minimal_record['locations'] = {
        'features': [{
            'geometry': {
                'type': 'Point',
                'coordinates': [6.052778, 46.234167]
            }
        }]
    }

    record = BibliographicRecord.create(minimal_record)

    # Dump it
    dump = record.dumps(dumper=dumper)

    # Centroid has been inferred
    assert (
        dump['locations']['features'][0]['centroid'] ==
        minimal_record['locations']['features'][0]['geometry']['coordinates']
    )

    # And it round-trips
    assert (
        record.loads(dump, loader=dumper)['locations'] ==
        minimal_record['locations']
    )


def test_locationsdumper_with_no_featurecollection(app, db, minimal_record):
    dumper = ElasticsearchDumper(
        extensions=[LocationsDumper()]
    )

    record = BibliographicRecord.create(minimal_record)

    # Dump it
    dump = record.dumps(dumper=dumper)


@unittest.mock.patch(
    'invenio_rdm_records.records.dumpers.locations.shapely',
    None
)
def test_locationsdumper_with_polygon_and_no_shapely(app, db, minimal_record):
    dumper = ElasticsearchDumper(
        extensions=[LocationsDumper()]
    )

    minimal_record['locations'] = {
        'features': [{
            'geometry': {
                'type': 'Polygon',
                'coordinates': [
                    [
                        [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0],
                        [100.0, 0.0],
                    ]
                ]
            }
        }],
    }

    record = BibliographicRecord.create(minimal_record)

    with pytest.warns(UserWarning):
        dump = record.dumps(dumper=dumper)

    assert 'centroid' not in dump['locations']['features'][0]


def test_locationsdumper_with_polygon_and_mock_shapely(
    app, db, minimal_record
):
    with unittest.mock.patch(
        'invenio_rdm_records.records.dumpers.locations.shapely'
    ) as shapely:
        dumper = ElasticsearchDumper(
            extensions=[LocationsDumper()]
        )

        minimal_record['locations'] = {
            'features': [{
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [
                        [
                            [100.0, 0.0], [101.0, 0.0], [101.0, 1.0],
                            [100.0, 1.0], [100.0, 0.0],
                        ]
                    ]
                }
            }],
        }

        record = BibliographicRecord.create(minimal_record)

        shape = unittest.mock.Mock()
        shape.centroid.x, shape.centroid.y = 100.5, 0.5
        shapely.geometry.shape.return_value = shape

        dump = record.dumps(dumper=dumper)

        shapely.geometry.shape.assert_called_once_with(
            minimal_record['locations']['features'][0]['geometry']
        )
        assert dump['locations']['features'][0]['centroid'] == [100.5, 0.5]


def test_locationsdumper_with_polygon_and_shapely(app, db, minimal_record):
    pytest.importorskip('shapely')

    dumper = ElasticsearchDumper(
        extensions=[LocationsDumper()]
    )

    # This also tests shapes with elevations
    minimal_record['locations'] = {
        'features': [{
            'geometry': {
                'type': 'Polygon',
                'coordinates': [
                    [
                        [100.0, 0.0, 10], [101.0, 0.0, 10], [101.0, 1.0, 30],
                        [100.0, 1.0, 30], [100.0, 0.0, 10],
                    ]
                ]
            }
        }],
    }

    record = BibliographicRecord.create(minimal_record)

    dump = record.dumps(dumper=dumper)

    # 3D geometries still lead to 2D centroids
    assert dump['locations']['features'][0]['centroid'] == [100.5, 0.5]
