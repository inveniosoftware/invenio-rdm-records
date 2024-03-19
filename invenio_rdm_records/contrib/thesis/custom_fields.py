# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Thesis specific custom fields.

Implements the following fields:

- thesis.university
- thesis.department
- thesis.type
"""
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import BaseCF
from marshmallow import fields
from marshmallow_utils.fields import SanitizedUnicode


class ThesisCF(BaseCF):
    """Nested custom field."""

    @property
    def field(self):
        """Thesis fields definitions."""
        return fields.Nested(
            {
                "university": SanitizedUnicode(),
                "department": SanitizedUnicode(),
                "type": SanitizedUnicode(),
            }
        )

    @property
    def mapping(self):
        """Thesis search mappings."""
        return {
            "type": "object",
            "properties": {
                "university": {"type": "keyword"},
                "department": {"type": "keyword"},
                "type": {"type": "keyword"},
            },
        }


THESIS_NAMESPACE = {
    # Thesis
    "thesis": "",
}

THESIS_CUSTOM_FIELDS = [
    ThesisCF(name="thesis:thesis"),
]

THESIS_CUSTOM_FIELDS_UI = {
    "section": _("Thesis"),
    "fields": [
        {
            "field": "thesis:thesis",
            "ui_widget": "Thesis",
            "props": {
                "label": _("Thesis"),
                "icon": "university",
                "university": {
                    "label": _("Awarding university"),
                    "placeholder": "",
                    "description": "",
                },
                "department": {
                    "label": _("Awarding department"),
                    "placeholder": "",
                    "description": "",
                },
                "type": {
                    "label": _("Thesis type"),
                    "placeholder": "PhD",
                    "description": "The type of thesis (e.g. Masters, PhD, Engineers, Bachelors)",
                },
            },
        }
    ],
}
