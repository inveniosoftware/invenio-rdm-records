# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base parsing functions for the various serializers."""
from marshmallow import Schema, missing, post_dump

from invenio_rdm_records.contrib.journal.custom_fields import DumpProcessorMixin


class BaseSchema(Schema):
    """BaseSchema for serializers in JSON."""

    def __init__(self, processors=None, **kwargs):
        """Initialize a new instance of the BaseSchema class.

        :param processors: A list of `DumpProcessorMixin` instances used to modify the serialized output, defaults to None.
        :type processors: list, optional
        :raises AssertionError: If any item in the `processors` list is not an instance of `DumpProcessorMixin`.
        """
        super().__init__()
        self.processors = processors or []
        assert all(isinstance(p, DumpProcessorMixin) for p in self.processors)

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

        access_location = obj["metadata"].get("locations", [])
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
        return [obj["metadata"]["title"]]

    def get_identifiers(self, obj):
        """Get identifiers."""
        items = []
        items.extend(i["identifier"] for i in obj["metadata"].get("identifiers", []))
        items.extend(p["identifier"] for p in obj.get("pids", {}).values())

        return items or missing

    def get_creators(self, obj):
        """Get creators."""
        return [c["person_or_org"]["name"] for c in obj["metadata"].get("creators", [])]

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

    @post_dump(pass_original=True)
    def post_dump_pipeline(self, data, original, many, **kwargs):
        """Applies a sequence of post-dump steps to the serialized data.

        This method defines a pipeline of post-dump processing steps that are applied to the serialized data after the
        schema has been dumped. The pipeline consists of processor instances that implement
        a `post_dump` method.

        :param data: The result of serialization.
        :param original: The original object that was serialized.
        :param many: Whether the serialization was done on a collection of objects.
        :param **kwargs: Any additional keyword arguments passed to the function.

        :returns: The result of the pipeline processing on the serialized data.
        """
        for processor in self.processors:
            # Data is assumed to be modified and returend by the processor
            data = processor.post_dump(data, original)
        return data
