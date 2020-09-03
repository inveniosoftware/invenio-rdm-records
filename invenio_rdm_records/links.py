# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record specific links."""

from flask import current_app
from invenio_records_resources.links import RecordLinkBuilder


class RecordSelfHtmlLinkBuilder(RecordLinkBuilder):
    """Builds record "self_html" link."""

    def __init__(self, config):
        """Constructor."""
        # NOTE: LinkBuilders are init in an app context now, so the below is
        #       fine
        super(RecordSelfHtmlLinkBuilder, self).__init__(
            key="self_html",
            route=(
                current_app.config.get("RECORDS_UI_ENDPOINTS", {})
                .get("recid", {})
                .get("route")
            ),
            action="read",
            permission_policy=config.permission_policy_cls
        )


class DraftSelfHtmlLinkBuilder(RecordLinkBuilder):
    """Builds draft "self_html" link."""

    def __init__(self, config):
        """Constructor."""
        super(DraftSelfHtmlLinkBuilder, self).__init__(
            key="self_html",
            route=(
                current_app.config.get("RDM_RECORDS_UI_EDIT_URL")
            ),
            action="read",
            permission_policy=config.permission_policy_cls
        )
