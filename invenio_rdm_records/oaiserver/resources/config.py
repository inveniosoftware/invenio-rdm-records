# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources configuration."""

import marshmallow as ma
from flask_babelex import lazy_gettext as _
from flask_resources import ResourceConfig

from invenio_records_resources.resources.records.args import SearchRequestArgsSchema


class OAIPMHServerSearchRequestArgsSchema(SearchRequestArgsSchema):
    """OAI-PMH request parameters."""

    managed = ma.fields.Boolean()

class OAIPMHServerResourceConfig(ResourceConfig):
    """OAI-PMH resource config."""

    # Blueprint configuration
    blueprint_name = "oaipmh-server"
    url_prefix = "/oaipmh"
    routes = {
        "set-prefix": "/sets",
        "list": "",
        "item": "/<id>",
        "format-prefix": "/formats"
    }

    # Request parsing
    request_read_args = {}
    request_view_args = {"id": ma.fields.Int()}
    request_search_args = OAIPMHServerSearchRequestArgsSchema
