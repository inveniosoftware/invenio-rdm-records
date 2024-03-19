# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Imprint specific custom fields.

Implements the following fields:
- imprint.isbn
- imprint.pages
- imprint.place
- imprint.title
- imprint.edition
"""

from idutils import is_isbn
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import BaseCF
from marshmallow import fields
from marshmallow_utils.fields import SanitizedUnicode


class ImprintCF(BaseCF):
    """Nested custom field."""

    @property
    def field(self):
        """Imprint fields definitions."""
        return fields.Nested(
            {
                "title": SanitizedUnicode(),
                "isbn": SanitizedUnicode(
                    validate=is_isbn,
                    error_messages={
                        "validator_failed": _("Please provide a valid ISBN.")
                    },
                ),
                "pages": SanitizedUnicode(),
                "place": SanitizedUnicode(),
                "edition": SanitizedUnicode(),
            }
        )

    @property
    def mapping(self):
        """Imprint search mappings."""
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}},
                },
                "isbn": {"type": "keyword"},
                "pages": {"type": "keyword"},
                "place": {"type": "keyword"},
                "edition": {"type": "keyword"},
            },
        }


IMPRINT_NAMESPACE = {
    # Imprint
    "imprint": None,
}


IMPRINT_CUSTOM_FIELDS = [ImprintCF(name="imprint:imprint")]

IMPRINT_CUSTOM_FIELDS_UI = {
    "section": _("Book / Report / Chapter"),
    "fields": [
        {
            "field": "imprint:imprint",
            "ui_widget": "Imprint",
            "template": "imprint.html",
            "props": {
                "label": _("Imprint (Book, Chapter, or Report)"),
                "place": {
                    "label": _("Place"),
                    "placeholder": _("e.g. city, country"),
                    "description": _("Place where the book or report was published"),
                },
                "isbn": {
                    "label": _("ISBN"),
                    "placeholder": _("e.g. 0-06-251587-X"),
                    "description": _("International Standard Book Number"),
                },
                "title": {
                    "label": _("Book or report title"),
                    "placeholder": "",
                    "description": _(
                        "Title of the book or report which this upload is part of"
                    ),
                },
                "pages": {
                    "label": _("Pagination"),
                    "placeholder": _("e.g. 15-23 or 158"),
                    "description": "",
                },
                "edition": {
                    "label": _("Edition"),
                    "placeholder": _("e.g. 3"),
                    "description": _("The edition of the book"),
                },
                "icon": "book",
            },
        }
    ],
}
