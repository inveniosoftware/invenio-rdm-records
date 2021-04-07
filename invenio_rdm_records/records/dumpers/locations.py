# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""ElasticSearch dumpers for location information."""

import warnings

from invenio_records.dumpers import ElasticsearchDumperExt

try:
    import shapely.geometry
except ImportError:
    shapely = None


class LocationsDumper(ElasticsearchDumperExt):
    """ElasticSearch dumper for location data.

    This does a few things:

    * Removes/adds FeatureCollection and Feature types, as those are
      constant
    * Calculates a centroid for each location if a geometry is provided

    Centroid calculation requires shapely, except for the simple case where
    the geometry is a point.
    """

    def dump(self, record, data):
        """Dump the data."""
        if 'locations' not in data.get('metadata', {}):
            return data
        for feature in data['metadata']['locations']['features']:
            geometry = feature.get('geometry')
            if geometry:
                if geometry['type'] == 'Point':
                    feature['centroid'] = geometry['coordinates']
                elif shapely:
                    centroid = shapely.geometry.shape(geometry).centroid
                    feature['centroid'] = [centroid.x, centroid.y]
                else:
                    warnings.warn(
                        "Trying to find centroid for non-point geometry, but "
                        "shapely isn't installed."
                    )

    def load(self, data, record_cls):
        """Load the data."""
        if 'locations' not in data.get('metadata', {}):
            return
        for feature in data['metadata']['locations']['features']:
            feature.pop('centroid', None)
