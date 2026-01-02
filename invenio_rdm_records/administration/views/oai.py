# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
# Copyright (C) 2023 Graz University of Technology.
# Copyright (C) 2024 KTH Royal Institute of Technology.
#
# invenio-administration is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio administration OAI-PMH view module."""

from invenio_administration.views.base import (
    AdminResourceCreateView,
    AdminResourceDetailView,
    AdminResourceEditView,
    AdminResourceListView,
)
from invenio_i18n import lazy_gettext as _


class OaiPmhListView(AdminResourceListView):
    """Configuration for OAI-PMH sets list view."""

    api_endpoint = "/oaipmh/sets"
    name = "OAI-PMH"
    resource_config = "oaipmh_server_resource"
    search_request_headers = {"Accept": "application/json"}
    title = _("OAI-PMH Sets")
    category = _("Site management")
    pid_path = "id"
    icon = "exchange"
    template = "invenio_rdm_records/oai-search.html"

    display_search = True
    display_delete = True
    display_edit = True

    item_field_list = {
        "spec": {"text": _("Set spec"), "order": 1},
        "name": {"text": _("Set name"), "order": 2},
        "search_pattern": {"text": _("Search query"), "order": 3},
        "created": {"text": _("Created"), "order": 4},
        "updated": {"text": _("Updated"), "order": 5},
    }

    search_config_name = "RDM_OAI_PMH_SEARCH"
    search_facets_config_name = "RDM_OAI_PMH_FACETS"
    search_sort_config_name = "RDM_OAI_PMH_SORT_OPTIONS"

    create_view_name = "oaipmh_create"
    resource_name = "name"


class OaiPmhEditView(AdminResourceEditView):
    """Configuration for OAI-PMH sets edit view."""

    name = "oaipmh_edit"
    url = "/oai-pmh/<pid_value>/edit"
    resource_config = "oaipmh_server_resource"
    pid_path = "id"
    api_endpoint = "/oaipmh/sets"
    title = _("Edit OAI-PMH set")

    list_view_name = _("OAI-PMH")

    form_fields = {
        "name": {
            "order": 1,
            "text": _("Set name"),
            "description": _("A short human-readable string naming the set."),
        },
        "spec": {
            "order": 2,
            "text": _("Set spec"),
            "description": _(
                "An identifier for the set, "
                "which cannot be edited after the set is created."
            ),
        },
        "search_pattern": {
            "order": 3,
            "text": _("Search query"),
            "description": _(
                "See the supported query "
                "syntax in the "
                "<a href='/help/search'>Search Guide</a>."
            ),
        },
        "created": {"order": 4},
        "updated": {"order": 5},
    }


class OaiPmhCreateView(AdminResourceCreateView):
    """Configuration for OAI-PMH sets create view."""

    name = "oaipmh_create"
    url = "/oai-pmh/create"
    resource_config = "oaipmh_server_resource"
    pid_path = "id"
    api_endpoint = "/oaipmh/sets"
    title = _("Create OAI-PMH set")

    list_view_name = _("OAI-PMH")

    form_fields = {
        "name": {
            "order": 1,
            "text": _("Set name"),
            "description": _("A short human-readable string naming the set."),
        },
        "spec": {
            "order": 2,
            "text": _("Set spec"),
            "description": _(
                "An identifier for the set, "
                "which cannot be edited after the set is created."
            ),
        },
        "search_pattern": {
            "order": 3,
            "text": _("Search query"),
            "description": _(
                "See the supported query "
                "syntax in the <a href='/help/search'>Search Guide</a>."
            ),
        },
    }


class OaiPmhDetailView(AdminResourceDetailView):
    """Configuration for OAI-PMH sets detail view."""

    url = "/oai-pmh/<pid_value>"
    api_endpoint = "/oaipmh/sets"
    search_request_headers = {"Accept": "application/json"}
    name = "OAI-PMH details"
    resource_config = "oaipmh_server_resource"
    title = _("OAI-PMH Details")

    template = "invenio_rdm_records/oai-details.html"
    display_delete = True
    display_edit = True

    list_view_name = _("OAI-PMH")
    pid_path = "id"

    item_field_list = {
        "name": {"text": _("Set name"), "order": 1},
        "spec": {"text": _("Set spec"), "order": 2},
        "search_pattern": {"text": _("Search query"), "order": 3},
        "created": {"text": _("Created"), "order": 4},
        "updated": {"text": _("Updated"), "order": 5},
    }
