#
# Copyright (C) 2023 CERN.
# Copyright (C) 2024 KTH Royal Institute of Technology.
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
from functools import partial

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import BaseCF
from marshmallow import fields
from marshmallow_utils.fields import IdentifierValueSet, SanitizedUnicode
from marshmallow_utils.schemas import IdentifierSchema

from ...services.schemas.metadata import _valid_url, record_identifiers_schemes


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
                    validate=_valid_url(error_msg=_("You must provide a valid URL.")),
                ),
                "identifiers": IdentifierValueSet(
                    fields.Nested(
                        partial(
                            IdentifierSchema, allowed_schemes=record_identifiers_schemes
                        )
                    )
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
                "identifiers": {
                    "type": "object",
                    "properties": {
                        "identifier": {"type": "keyword"},
                        "schema": {"type": "keyword"},
                    },
                },
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
                "identifiers": {
                    "label": _("Identifiers"),
                    "description": _("URL of conference website or other identifier."),
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
