# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019 Northwestern University.
# Copyright (C) 2021-2023 Graz University of Technology.
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio administration users view module."""
from functools import partial

from flask import current_app
from invenio_administration.views.base import (
    AdminResourceDetailView,
    AdminResourceListView,
)
from invenio_i18n import lazy_gettext as _

class JobsListView(AdminResourceListView):
    """Configuration for Jobs list view."""

    api_endpoint = "/jobs"
    extension_name = "invenio-rdm-records"
    name = "jobs"
    resource_config = "jobs_resource"
    title = "Jobs"
    menu_label = "Jobs"
    category = "System"
    pid_path = "id"
    icon = "settings"

    display_search = False
    display_delete = False
    display_edit = False
    display_create = False

    item_field_list = {
        "job": {"text": _("Jobs"), "order": 1, "width":3},
        "last_run_start_time": {"text": _("Last run"), "order": 2, "width":3},
        "last_run_status": {"text": _("Status"), "order": 3, "width":1},
        "user": {"text": _("Started by"), "order": 4, "width":3},
        "next_run": {"text": _("Next run"), "order": 5, "width":3},
    }

    search_config_name = "RDM_JOBS_SEARCH"
    search_sort_config_name = "RDM_JOBS_SORT_OPTIONS"
    search_facets_config_name = "RDM_JOBS_FACETS"
    template = "invenio_rdm_records/system/jobs/jobs-search.html"
    
    actions = {
        "settings": {
            "text": "Settings",
            "payload_schema": None,
            "order": 1,
            "icon": "star"
        },
        "schedule": {
            "text": "Schedule",
            "payload_schema": None,
            "order": 2,
        },
        "run": {
            "text": "Run Now",
            "payload_schema": None,
            "order": 2,
        }
    }


class JobsDetailView(AdminResourceDetailView):
    """Configuration for Jobs detail view."""

    url = "/jobs/<pid_value>"
    api_endpoint = "/jobs"
    search_request_headers = {"Accept": "application/json"}
    name = "Job Details"
    resource_config = "jobs_resource"
    title = "Job Details"

    template =  "invenio_rdm_records/system/jobs/jobs-details.html"
    display_delete = False
    display_edit = False
    display_search = False

    list_view_name = "jobs"
    pid_path = "id"

    item_field_list = {
        "run": {"text": _("Runs"), "order": 1},
        "duration": {"text": _("Duration"), "order": 2},
        "message": {"text": _("Message"), "order": 3},
        "user": {"text": _("Started by"), "order": 4},
    }
