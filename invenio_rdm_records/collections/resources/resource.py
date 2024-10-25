# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collection resource."""

from flask import g
from flask_resources import Resource, resource_requestctx, response_handler, route
from invenio_records_resources.resources.records.resource import (
    request_search_args,
    request_view_args,
)


class CollectionsResource(Resource):
    """Collection resource."""

    def __init__(self, config, service):
        """Instantiate the resource."""
        super().__init__(config)
        self.service = service

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        return [
            route("GET", routes["search-records"], self.search_records),
        ]

    @request_view_args
    @request_search_args
    @response_handler(many=True)
    def search_records(self):
        """Search records in a collection."""
        id_ = resource_requestctx.view_args["id"]
        records = self.service.search_collection_records(
            g.identity,
            id_,
            params=resource_requestctx.args,
        )
        return records.to_dict(), 200
