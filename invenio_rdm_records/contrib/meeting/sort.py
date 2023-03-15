# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

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
