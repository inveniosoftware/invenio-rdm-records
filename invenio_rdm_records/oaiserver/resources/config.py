# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OAI-PMH resource configuration."""

import marshmallow as ma
from flask_resources import HTTPJSONException, ResourceConfig, create_error_handler
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.args import SearchRequestArgsSchema
from invenio_records_resources.services.base.config import ConfiguratorMixin

from ..services.errors import (
    OAIPMHError,
    OAIPMHSetDoesNotExistError,
    OAIPMHSetIDDoesNotExistError,
)

oaipmh_error_handlers = {
    **ErrorHandlersMixin.error_handlers,
    OAIPMHSetDoesNotExistError: create_error_handler(
        lambda e: HTTPJSONException(
            code=404,
            description=e.description,
        )
    ),
    OAIPMHSetIDDoesNotExistError: create_error_handler(
        lambda e: HTTPJSONException(
            code=404,
            description=e.description,
        )
    ),
    OAIPMHError: create_error_handler(
        lambda e: HTTPJSONException(
            code=400,
            description=e.description,
        )
    ),
}


class OAIPMHServerSearchRequestArgsSchema(SearchRequestArgsSchema):
    """OAI-PMH request parameters."""

    managed = ma.fields.Boolean()
    sort_direction = ma.fields.Str()


class OAIPMHServerResourceConfig(ResourceConfig, ConfiguratorMixin):
    """OAI-PMH resource config."""

    # Blueprint configuration
    blueprint_name = "oaipmh-server"
    url_prefix = "/oaipmh"
    routes = {
        "set-prefix": "/sets",
        "list": "",
        "item": "/<id>",
        "format-prefix": "/formats",
    }

    # Request parsing
    request_read_args = {}
    request_view_args = {"id": ma.fields.Int()}
    request_search_args = OAIPMHServerSearchRequestArgsSchema

    error_handlers = oaipmh_error_handlers

    response_handlers = {
        "application/vnd.inveniordm.v1+json": ResourceConfig.response_handlers[
            "application/json"
        ],
        **ResourceConfig.response_handlers,
    }
