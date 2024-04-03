# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Convenient URL generation.

InvenioRDM poses challenges to url generation that Flask's url_for cannot handle out
of the gate.

- InvenioRDM is actually 2 applications mounted on different url_prefixes:
  `url_for` in the API application isn't aware of the UI application endpoints
- The routes are configurable via the `APP_RDM_ROUTES` configuration.
- But `APP_RDM_ROUTES` is not used for `RDMRecordServiceConfig.links_item` leading to
  conflicts and inconsistencies.
- The endpoint names are relatively hidden / spread out and APP_RDM_ROUTES does have
  its own endpoint naming convention.
- All other url generation use cases need to interact with this: generating urls outside
  of a request context, generating canonical urls...

This module contains minimal methods to generate URLs correctly without much
engineering. Over time, it can be made more abstract, complex and powerful and even
extracted into its own package to solve url generation across InvenioRDM once and for
all.
"""

from flask import current_app


def record_url_for(_app="ui", pid_value=""):
    """Return url for record route."""
    assert _app in ["ui", "api"]

    site_app = _app.upper()
    url_prefix = current_app.config.get(f"SITE_{site_app}_URL", "")

    # We use [] so that this fails and brings to attention the configuration
    # problem if APP_RDM_ROUTES.record_detail is missing
    url_path = current_app.config["APP_RDM_ROUTES"]["record_detail"].replace(
        "<pid_value>", pid_value
    )

    return "/".join(p.strip("/") for p in [url_prefix, url_path])


def download_url_for(pid_value="", filename=""):
    """Return url for download route."""
    url_prefix = current_app.config.get("SITE_UI_URL", "")

    # We use [] so that this fails and brings to attention the configuration
    # problem if APP_RDM_ROUTES.record_file_download is missing
    url_path = (
        current_app.config["APP_RDM_ROUTES"]["record_file_download"]
        .replace("<pid_value>", pid_value)
        .replace("<path:filename>", filename)
    )

    return "/".join(p.strip("/") for p in [url_prefix, url_path])
