# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021 data-futures.
# Copyright (C) 2022 Universität Hamburg.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Resource."""
from flask import abort, redirect, url_for
from flask_resources import Resource, response_handler, route
from invenio_drafts_resources.resources import RecordResource
from invenio_records_resources.resources.records.resource import (
    request_extra_args,
    request_search_args,
    request_view_args,
)
from invenio_records_resources.resources.records.utils import search_preference
from invenio_stats import current_stats
from sqlalchemy.exc import NoResultFound


class JobsResource(RecordResource):
    """RDM job resource."""

    def create_url_rules(self):
        """Create the URL rules for the record resource."""

        routes = self.config.routes
        url_rules = super().create_url_rules()
        url_rules += [
            route("GET", routes["list"], self.search),
        ]

        return url_rules
