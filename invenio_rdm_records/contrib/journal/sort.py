# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Journal sorting."""

from invenio_i18n import lazy_gettext as _

JOURNAL_SORT_OPTIONS = {
    "journal-desc": {
        "title": _("Journal [Newest]"),
        "fields": [
            "-metadata.publication_date",
            "custom_fields.journal:journal.volume",
            "custom_fields.journal:journal.issue",
            "custom_fields.journal:journal.pages",
        ],
    },
}
