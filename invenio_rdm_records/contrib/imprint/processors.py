# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
# Copyright (C) 2023 Caltech.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Imprint serialization processing."""

from flask_resources.serializers import DumperMixin


class ImprintCSLDumper(DumperMixin):
    """Dumper for CSL serialization of 'Imprint' custom field."""

    def post_dump(self, data, original=None, **kwargs):
        """Adds serialized journal data to the input data."""
        _original = original or {}
        custom_fields = _original.get("custom_fields", {})
        imprint_data = custom_fields.get("imprint:imprint", {})

        if not imprint_data:
            return data

        title = imprint_data.get("title")
        place = imprint_data.get("place")
        pages = imprint_data.get("pages")
        isbn = imprint_data.get("isbn")

        if title:
            data["container_title"] = title
        if pages:
            data["page"] = pages
        if place:
            data["publisher_place"] = place
        if isbn:
            data["ISBN"] = isbn

        return data


class ImprintMarcXMLDumper(DumperMixin):
    """Dumper for MarcXML serialization of 'Imprint' custom field."""

    def post_dump(self, data, original=None, **kwargs):
        """Adds serialized imprint data to the input data under the '773' key."""
        _original = original or {}
        custom_fields = _original.get("custom_fields", {})
        imprint_data = custom_fields.get("imprint:imprint", {})

        if not imprint_data:
            return data

        items_dict = {}
        field_keys = {
            "t": imprint_data.get("title"),
            "z": imprint_data.get("isbn"),
            "g": imprint_data.get("pages"),
            "a": imprint_data.get("place"),
            "b": _original.get("metadata", {}).get("publication_date"),
        }
        for key, value in field_keys.items():
            if value:
                items_dict[key] = value

        if not items_dict:
            return data

        code = "773  "
        existing_data = data.get(code)
        if existing_data and isinstance(existing_data, list):
            data[code].append(items_dict)
        else:
            data[code] = [items_dict]
        return data
