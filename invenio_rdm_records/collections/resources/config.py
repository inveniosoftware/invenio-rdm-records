# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Collection resource config."""

from flask_resources import (
    HTTPJSONException,
    JSONSerializer,
    ResourceConfig,
    ResponseHandler,
    create_error_handler,
)
from invenio_records_resources.resources.records.args import SearchRequestArgsSchema
from invenio_records_resources.resources.records.headers import etag_headers
from marshmallow.fields import Integer

from invenio_rdm_records.resources.serializers import UIJSONSerializer

from ..errors import CollectionNotFound


class CollectionsResourceConfig(ResourceConfig):
    """Configuration for the Collection resource."""

    blueprint_name = "collections"
    url_prefix = "/collections"

    routes = {
        "search-records": "/<id>/records",
    }

    request_view_args = {"id": Integer()}
    request_search_args = SearchRequestArgsSchema
    error_handlers = {
        CollectionNotFound: create_error_handler(
            HTTPJSONException(
                code=404,
                description="Collection was not found.",
            )
        ),
    }
    response_handlers = {
        "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
        "application/vnd.inveniordm.v1+json": ResponseHandler(
            UIJSONSerializer(), headers=etag_headers
        ),
    }
