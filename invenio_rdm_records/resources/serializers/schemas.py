# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base parsing functions for the various serializers."""

from marshmallow import missing
from pydash import py_


class CommonFieldsMixin:
    """Common fields serialization."""

    def get_doi(self, obj):
        """Get DOI."""
        if "doi" in obj["pids"]:
            return obj["pids"]["doi"]["identifier"]

        for identifier in obj["metadata"].get("identifiers", []):
            if identifier["scheme"] == "doi":
                return identifier["identifier"]

        return missing

    def get_locations(self, obj):
        """Get locations."""
        locations = []

        access_location = obj["metadata"].get("locations", {})

        if not access_location:
            return missing

        for location in access_location.get("features", []):
            location_string = ""

            place = location.get("place")
            description = location.get("description")
            if place:
                location_string += f"name={place}; "
            if description:
                location_string += f"description={description}"
            geometry = location.get("geometry")
            if geometry:
                geo_type = geometry["type"]
                if geo_type == "Point":
                    coords = geometry["coordinates"]
                    location_string += f"; lat={coords[0]}; lon={coords[1]}"

            locations.append(location_string)

        return locations

    def get_titles(self, obj):
        """Get titles."""
        title = py_.get(obj, "metadata.title")
        return [title] if title else missing

    def get_identifiers(self, obj):
        """Get identifiers."""
        items = []
        items.extend(i["identifier"] for i in obj["metadata"].get("identifiers", []))
        items.extend(p["identifier"] for p in obj.get("pids", {}).values())

        return items or missing

    def get_creators(self, obj):
        """Get creators."""
        return [
            c["person_or_org"]["name"] for c in obj["metadata"].get("creators", [])
        ] or missing

    def get_publishers(self, obj):
        """Get publishers."""
        publisher = obj["metadata"].get("publisher")
        if publisher:
            return [publisher]
        return missing

    def get_contributors(self, obj):
        """Get contributors."""
        return [
            c["person_or_org"]["name"] for c in obj["metadata"].get("contributors", [])
        ] or missing
