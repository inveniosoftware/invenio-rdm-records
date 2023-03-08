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

from idutils import is_issn
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
                "issn": SanitizedUnicode(
                    validate=is_issn,
                    error_messages={
                        "validator_failed": _("Please provide a valid ISSN.")
                    },
                ),
            }
        )

    @property
    def mapping(self):
        """Journal search mappings."""
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}},
                },
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
                    "placeholder": "",
                    "description": _(
                        "Title of the journal on which the article was published"
                    ),
                },
                "volume": {
                    "label": _("Volume"),
                    "placeholder": "",
                    "description": "",
                },
                "issue": {
                    "label": _("Issue"),
                    "placeholder": "",
                    "description": "",
                },
                "pages": {
                    "label": _("Pages"),
                    "placeholder": "",
                    "description": "",
                },
                "issn": {
                    "label": _("ISSN"),
                    "placeholder": "",
                    "description": _("International Standard Serial Number"),
                },
                "icon": "newspaper outline",
            },
        }
    ],
}
