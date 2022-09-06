# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# invenio-administration is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio administration OAI-PMH view module."""
from invenio_administration.views.base import AdminResourceListView,\
    AdminResourceEditView, AdminResourceCreateView


class OaiPmhListView(AdminResourceListView):

    api_endpoint = "/oaipmh/sets"
    search_request_headers = {"Accept": "application/json"}
    name = "OAI-PMH"
    resource_config = "oaipmh_server_resource"
    title = "OAI-PMH Sets"
    category = "Site management"
    pid_path = "id"

    # OAI sets are not searchable in ES
    display_search = False
    display_delete = True

    item_field_list = {
        "id": {
          "text": "ID",
          "order": 1
        },
        "name": {
            "text": "Title",
            "order": 2
        },
        "spec": {
            "text": "Spec",
            "order": 3
        },
        "search_pattern": {
            "text": "Search Query",
            "order": 4
        },
        "updated": {
            "text": "Modified",
            "order": 5
        }
    }

    search_config_name = "RDM_OAI_PMH_SEARCH"
    search_facets_config_name = "RDM_OAI_PMH_FACETS"
    search_sort_config_name = "RDM_OAI_PMH_SORT_OPTIONS"

    create_view_name = "oaipmh_create"
    list_view_name = "OAI-PMH"


class OaiPmhEditView(AdminResourceEditView):

    name = "oaipmh_edit"
    url = "/oai-pmh/<pid_value>/edit"
    resource_config = "oaipmh_server_resource"
    pid_path = "id"
    api_endpoint = "/oaipmh/sets"
    title = "Edit OAI-PMH set"

    list_view_name = "OAI-PMH"


class OaiPmhCreateView(AdminResourceCreateView):

    name = "oaipmh_create"
    url = "/oai-pmh/create"
    resource_config = "oaipmh_server_resource"
    pid_path = "id"
    api_endpoint = "/oaipmh/sets"
    title = "Create OAI-PMH set"

    list_view_name = "OAI-PMH"
