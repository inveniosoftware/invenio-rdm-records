# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""GeoJSON based Schema for Invenio RDM Records."""

from marshmallow import Schema, fields


class GeoJSONSchema(Schema):
    """Schema for GeoJSON in JSON."""

    features = fields.Method("get_locations")
    type = fields.Constant(
        "FeatureCollection", dump_to="type"
    )  # Will always return Feature Collection, even though there may be just 1 point

    def get_locations(self, obj):
        """Get locations."""
        items = []

        if "locations" not in obj["metadata"]:
            return items

        for dict in obj["metadata"]["locations"]["features"]:
            item = {
                "type": "Feature",
                "geometry": {
                    "type": dict["geometry"]["type"],
                    "coordinates": dict["geometry"]["coordinates"],
                },
                "properties": {
                    key: dict[key] for key in dict if key != "geometry"
                },  # Done in oder to include all "non-necessary" fields
            }
            items.append(item)
        return items
