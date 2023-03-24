# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base parsing functions for the various serializers."""
from marshmallow import Schema, missing, post_dump, post_load, pre_dump, pre_load

from invenio_rdm_records.contrib.journal.custom_fields import FieldDumper, FieldLoader


class CommonFieldsMixin(object):
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


class DumperMixin(Schema):
    """A mixin that adds post-dump and pre-dump processing functionality to the `Schema` class.

    This mixin provides a way to modify the serialized or deserialized output of a schema after or before it has been dumped.
    """

    def __init__(self, dumpers=None, **kwargs):
        """Initialize a new instance of the `DumperMixin` class.

        :param dumpers: A list of `DumpProcessorMixin` instances used to modify the serialized output, defaults to None.
        :type dumpers: list, optional
        :raises AssertionError: If any item in the `dumpers` list is not an instance of `DumpProcessorMixin`.
        """
        super().__init__(**kwargs)
        self.dumpers = dumpers or []
        assert all(isinstance(p, FieldDumper) for p in self.dumpers)

    @post_dump(pass_original=True)
    def post_dump_pipeline(self, data, original, many, **kwargs):
        """Applies a sequence of post-dump steps to the serialized data.

        This method defines a pipeline consisting of `DumpProcessorMixin` instances that implement a `post_dump` method.

        :param data: The result of serialization.
        :param original: The original object that was serialized.
        :param many: Whether the serialization was done on a collection of objects.

        :returns: The result of the pipeline processing on the serialized data.
        """
        for dumper in self.dumpers:
            # Data is assumed to be modified and returned by the dumper
            data = dumper.post_dump(data, original)
        return data

    @pre_dump
    def pre_dump_pipeline(self, data, many, **kwargs):
        """Applies a sequence of pre-dump steps to the input data.

        This method defines a pipeline consisting of `DumpProcessorMixin` instances that implement a `pre_dump` method.

        :param data: The result of serialization.
        :param many: Whether the serialization was done on a collection of objects.

        :returns: The result of the pipeline processing on the serialized data.
        """
        for dumper in self.dumpers:
            # Data is assumed to be modified and returned by the dumper
            data = dumper.pre_dump(data)
        return data


class LoaderMixin(Schema):
    def __init__(self, loaders=None, **kwargs):
        """Initialize a new instance of the `LoaderMixin` class.

        :param loaders: A list of `LoadProcessorMixin` instances used to modify the serialized output, defaults to None.
        :type loaders: list, optional
        :raises AssertionError: If any item in the `loaders` list is not an instance of `LoadProcessorMixin`.
        """
        super().__init__(**kwargs)
        self.loaders = loaders or []
        assert all(isinstance(p, FieldLoader) for p in self.loaders)

    @post_load(pass_original=True)
    def post_load_pipeline(self, data, original, many, **kwargs):
        """Applies a sequence of post-load steps to the serialized data.

        This method defines a pipeline consisting of `LoadProcessorMixin` instances that implement a `post_load` method.

        :param data: The result of deserialization.
        :param original: The original object that was serialized.
        :param many: Whether the deserialization was done on a collection of objects.

        :returns: The result of the pipeline processing on the deserialized data.
        """
        for loader in self.loaders:
            # Data is assumed to be modified and returned by the loader
            data = loader.post_load(data, original)
        return data

    @pre_load
    def pre_load_pipeline(self, data, many, **kwargs):
        """Applies a sequence of pre-dump steps to the input data.

        This method defines a pipeline consisting of `DumpProcessorMixin` instances that implement a `pre_dump` method.

        :param data: The result of serialization.
        :param many: Whether the serialization was done on a collection of objects.

        :returns: The result of the pipeline processing on the serialized data.
        """
        for dumper in self.loaders:
            # Data is assumed to be modified and returned by the loader
            data = dumper.pre_load(data)
        return data
