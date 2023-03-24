#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Meeting custom fields.

Implements the following fields:

- meeting.acronym
- meeting.dates
- meeting.place
- meeting.session_part
- meeting.session
- meeting.title
- meeting.url
"""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import BaseCF
from marshmallow import fields
from marshmallow_utils.fields import SanitizedUnicode

from invenio_rdm_records.contrib.journal.custom_fields import FieldDumper
from invenio_rdm_records.services.schemas.metadata import _valid_url


class MeetingDublinCoreDumper(FieldDumper):
    """Dump processor for dublin core serialization of 'Meeting' custom field."""

    def post_dump(self, data, original=None, **kwargs):
        """Adds serialized meeting data to the input data under the 'sources' key."""
        _original = original or {}
        custom_fields = _original.get("custom_fields", {})
        meeting_data = custom_fields.get("meeting:meeting", {})

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


class MeetingCF(BaseCF):
    """Nested custom field."""

    @property
    def field(self):
        """Meeting fields definitions."""
        return fields.Nested(
            {
                "acronym": SanitizedUnicode(),
                "dates": SanitizedUnicode(),
                "place": SanitizedUnicode(),
                "session_part": SanitizedUnicode(),
                "session": SanitizedUnicode(),
                "title": SanitizedUnicode(),
                "url": SanitizedUnicode(
                    validate=_valid_url(error_msg="You must provide a valid URL."),
                ),
            }
        )

    @property
    def mapping(self):
        """Meeting search mappings."""
        return {
            "type": "object",
            "properties": {
                "acronym": {"type": "keyword"},
                "dates": {"type": "keyword"},
                "place": {"type": "text"},
                "session_part": {"type": "keyword"},
                "session": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}},
                },
                "url": {"type": "keyword"},
            },
        }


MEETING_NAMESPACE = {
    # Meeting
    "meeting": "",
}


MEETING_CUSTOM_FIELDS = [
    MeetingCF(name="meeting:meeting"),
]

MEETING_CUSTOM_FIELDS_UI = {
    "section": _("Conference"),
    "fields": [
        {
            "field": "meeting:meeting",
            "ui_widget": "Meeting",
            "template": "meeting.html",
            "props": {
                "title": {
                    "label": _("Title"),
                    "placeholder": "",
                    "description": "",
                },
                "acronym": {
                    "label": _("Acronym"),
                    "placeholder": "",
                    "description": "",
                },
                "dates": {
                    "label": _("Dates"),
                    "placeholder": _("e.g. 21-22 November 2022."),
                    "description": "",
                },
                "place": {
                    "label": _("Place"),
                    "placeholder": "",
                    "description": _("Location where the conference took place."),
                },
                "url": {
                    "label": _("Website"),
                    "placeholder": "",
                    "description": "",
                },
                "session": {
                    "label": _("Session"),
                    "placeholder": _("e.g. VI"),
                    "description": _("Session within the conference."),
                },
                "session_part": {
                    "label": _("Part"),
                    "placeholder": _("e.g. 1"),
                    "description": _("Part within the session."),
                },
            },
        }
    ],
}
