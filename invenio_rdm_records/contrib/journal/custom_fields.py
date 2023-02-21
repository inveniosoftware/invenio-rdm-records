#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Journal custom fields.

Implements the following fields:
- journal.issue
- journal.pages
- journal.title
- journal.volume
"""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import BaseCF
from invenio_records_resources.services.records.facets import CFTermsFacet
from marshmallow import fields
from marshmallow_utils.fields import SanitizedUnicode


class JournalCF(BaseCF):
    """Nested custom field."""

    @property
    def field(self):
        """Journal fields definitions."""
        return fields.Nested(
            {
                "title": SanitizedUnicode(),
                "issue": SanitizedUnicode(),
                "volume": SanitizedUnicode(),
                "pages": SanitizedUnicode(),
                "issn": SanitizedUnicode(),
            }
        )

    @property
    def mapping(self):
        """Journal search mappings."""
        return {
            "type": "object",
            "properties": {
                "title": {"type": "keyword"},
                "issue": {"type": "keyword"},
                "pages": {"type": "keyword"},
                "volume": {"type": "keyword"},
                "issn": {"type": "keyword"},
            },
        }


JOURNAL_NAMESPACE = {
    # Journal
    "journal": "",
}


JOURNAL_CUSTOM_FIELDS = [
    JournalCF(name="journal:journal"),
]

JOURNAL_CUSTOM_FIELDS_UI = {
    "section": _("Journal"),
    "fields": [
        {
            "field": "journal:journal",
            "ui_widget": "Journal",
            "template": "journal.html",
            "props": {
                "label": _("Journal"),
                "title": {
                    "label": _("Title"),
                    "placeholder": _(""),
                    "description": _("Journal title"),
                },
                "volume": {
                    "label": _("Volume"),
                    "placeholder": _(""),
                    "description": _("Journal volume"),
                },
                "issue": {
                    "label": _("Issue"),
                    "placeholder": _(""),
                    "description": _("Journal issue"),
                },
                "pages": {
                    "label": _("Pages"),
                    "placeholder": _(""),
                    "description": _(
                        "Journal pages on which this record was published"
                    ),
                },
                "issn": {
                    "label": _("ISSN"),
                    "placeholder": _(""),
                    "description": _(
                        "Journal International Standard Serial Number (ISSN)"
                    ),
                },
                "icon": "lab",
                "description": "Journal in which this record was published.",
            },
        }
    ],
}
