# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Meeting sorting."""

from invenio_i18n import lazy_gettext as _

MEETING_SORT_OPTIONS = {
    "conference-desc": {
        "title": _("Conference session [Newest]"),
        "fields": [
            "-custom_fields.meeting:meeting.session",
            "-custom_fields.meeting:meeting.session_part",
        ],
    },
}
