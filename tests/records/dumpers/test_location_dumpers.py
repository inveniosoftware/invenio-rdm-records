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

from invenio_rdm_records.records import RDMRecord
from invenio_rdm_records.records.dumpers import LocationsDumper


def test_locationsdumper_with_point_geometry(app, db, minimal_record, parent):
    dumper = ElasticsearchDumper(
        extensions=[LocationsDumper()]
    )

    minimal_record['metadata']['locations'] = {
        'features': [{
            'geometry': {
                'type': 'Point',
                'coordinates': [6.052778, 46.234167]
            }
        }]
    }

    record = RDMRecord.create(minimal_record, parent=parent)

    # Dump it
    dump = record.dumps(dumper=dumper)

    # Centroid has been inferred
    dumped_feature = dump['metadata']['locations']['features'][0]
    expected_feature = minimal_record['metadata']['locations']['features'][0]
    assert (
        dumped_feature['centroid'] ==
        expected_feature['geometry']['coordinates']
    )

    # And it round-trips
    assert (
        record.loads(dump, loader=dumper)['metadata']['locations'] ==
        minimal_record['metadata']['locations']
    )


def test_locationsdumper_with_no_featurecollection(
        app, db, minimal_record, parent):
    dumper = ElasticsearchDumper(
        extensions=[LocationsDumper()]
    )

    record = RDMRecord.create(minimal_record, parent=parent)

    # Dump it
    dump = record.dumps(dumper=dumper)


@unittest.mock.patch(
    'invenio_rdm_records.records.dumpers.locations.shapely',
    None
)
def test_locationsdumper_with_polygon_and_no_shapely(
        app, db, minimal_record, parent):
    dumper = ElasticsearchDumper(
        extensions=[LocationsDumper()]
    )

    minimal_record['metadata']['locations'] = {
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

    record = RDMRecord.create(minimal_record, parent=parent)

    with pytest.warns(UserWarning):
        dump = record.dumps(dumper=dumper)

    assert 'centroid' not in dump['metadata']['locations']['features'][0]


def test_locationsdumper_with_polygon_and_mock_shapely(
    app, db, minimal_record, parent
):
    with unittest.mock.patch(
        'invenio_rdm_records.records.dumpers.locations.shapely'
    ) as shapely:
        dumper = ElasticsearchDumper(
            extensions=[LocationsDumper()]
        )

        minimal_record['metadata']['locations'] = {
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

        record = RDMRecord.create(minimal_record, parent=parent)

        shape = unittest.mock.Mock()
        shape.centroid.x, shape.centroid.y = 100.5, 0.5
        shapely.geometry.shape.return_value = shape

        dump = record.dumps(dumper=dumper)

        shapely.geometry.shape.assert_called_once_with(
            minimal_record['metadata']['locations']['features'][0]['geometry']
        )
        assert dump['metadata']['locations']['features'][0]['centroid'] == \
            [100.5, 0.5]


def test_locationsdumper_with_polygon_and_shapely(
        app, db, minimal_record, parent):
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

    record = RDMRecord.create(minimal_record, parent=parent)

    dump = record.dumps(dumper=dumper)

    # 3D geometries still lead to 2D centroids
    assert dump['locations']['features'][0]['centroid'] == [100.5, 0.5]
