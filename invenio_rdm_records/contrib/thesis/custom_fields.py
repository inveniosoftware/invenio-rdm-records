# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Thesis specific custom fields.

Implements the following fields:

- thesis.university
"""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.custom_fields import TextCF

THESIS_NAMESPACE = {
    # Thesis
    "thesis": None,
}

THESIS_CUSTOM_FIELDS = [
    TextCF(name="thesis:university"),
]

THESIS_CUSTOM_FIELDS_UI = {
    "section": _("Thesis"),
    "fields": [
        {
            "field": "thesis:university",
            "ui_widget": "Thesis",
            "props": {
                "label": _("Thesis"),
                "icon": "university",
                "university": {
                    "label": _("Awarding university"),
                    "placeholder": "",
                    "description": "",
                },
            },
        }
    ],
}
