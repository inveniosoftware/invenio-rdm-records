#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Meeting serialization processing."""

from flask_resources.serializers import DumperMixin


class MeetingDublinCoreDumper(DumperMixin):
    """Dumper for dublin core serialization of 'Meeting' custom field."""

    def post_dump(self, data, original=None, **kwargs):
        """Adds serialized meeting data to the input data under the 'sources' key."""
        _original = original or {}
        custom_fields = _original.get("custom_fields", {})
        meeting_data = custom_fields.get("meeting:meeting", {})

        if not meeting_data:
            return data

        parts = [
            meeting_data.get("acronym"),
            meeting_data.get("title"),
            meeting_data.get("place"),
            meeting_data.get("dates"),
        ]

        # Update input data with serialized data
        serialized_data = ", ".join([x for x in parts if x])
        sources = data.get("sources", [])
        sources.append(serialized_data)
        data["sources"] = sources

        return data


class MeetingCSLDumper(DumperMixin):
    """Dumper for CSL serialization of 'Meeting' custom field."""

    def post_dump(self, data, original=None, **kwargs):
        """Adds serialized meeting data to the input data."""
        _original = original or {}
        custom_fields = _original.get("custom_fields", {})
        meeting_data = custom_fields.get("meeting:meeting", {})

        if not meeting_data:
            return data

        title = meeting_data.get("title")
        acronym = meeting_data.get("acronym")
        place = meeting_data.get("place")

        if title and acronym:
            data["event"] = f"{title} ({acronym})"
        elif title or acronym:
            data["event"] = title or acronym
        if place:
            data["event_place"] = place

        return data
