# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Notes specific custom fields.

Implements the following field:
- notes (additional notes)
"""

from flask_babelex import _
from invenio_records_resources.services.custom_fields import TextCF
from marshmallow import validate

NOTES_NAMESPACE = {
    # Notes
    "notes": "",
}


NOTES_CUSTOM_FIELDS = [
    TextCF(
        name="notes:notes",
    )
]

NOTES_CUSTOM_FIELDS_UI = {
    "section": _("Notes"),
    "fields": [
        dict(
            field="notes:notes",
            ui_widget="Input",
            props=dict(
                label="Additional notes",
                icon="pencil",
                description="Additional notes related with the record",
            ),
        ),
    ],
}
