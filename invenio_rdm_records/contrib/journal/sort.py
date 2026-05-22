# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

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
