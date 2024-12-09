# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collection search app helpers for React-SearchKit."""


from functools import partial

from flask import current_app
from invenio_search_ui.searchconfig import search_app_config


def search_app_context():
    """Search app context."""
    return {
        "search_app_collection_config": partial(
            search_app_config,
            config_name="RDM_SEARCH",
            available_facets=current_app.config["RDM_FACETS"],
            sort_options=current_app.config["RDM_SORT_OPTIONS"],
            headers={"Accept": "application/vnd.inveniordm.v1+json"},
            pagination_options=(10, 25, 50, 100),
        )
    }
