# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources configuration."""


import marshmallow as ma
from citeproc_styles import StyleNotFoundError
from flask_resources import HTTPJSONException, JSONSerializer, \
    ResponseHandler, create_error_handler, resource_requestctx
from invenio_drafts_resources.resources import RecordResourceConfig
from invenio_records_resources.resources.files import FileResourceConfig

from invenio_rdm_records.resources.args import RDMSearchRequestArgsSchema
from invenio_rdm_records.resources.serializers.dublincore import \
    DublinCoreXMLSerializer

from .serializers import CSLJSONSerializer, DataCite43JSONSerializer, \
    DataCite43XMLSerializer, StringCitationSerializer, UIJSONSerializer


def csl_url_args_retriever():
    """Returns the style and locale passed as URL args for CSL export."""
    style = resource_requestctx.args.get("style")
    locale = resource_requestctx.args.get("locale")
    return style, locale


#
# Response handlers
#
record_serializers = {
    "application/json": ResponseHandler(JSONSerializer()),
    "application/vnd.inveniordm.v1+json": ResponseHandler(UIJSONSerializer()),
    "application/vnd.citationstyles.csl+json": ResponseHandler(
        CSLJSONSerializer()
    ),
    "application/vnd.datacite.datacite+json": ResponseHandler(
        DataCite43JSONSerializer()
    ),
    "application/vnd.datacite.datacite+xml": ResponseHandler(
        DataCite43XMLSerializer()
    ),
    "application/x-dc+xml": ResponseHandler(DublinCoreXMLSerializer()),
    "text/x-bibliography": ResponseHandler(
        StringCitationSerializer(url_args_retriever=csl_url_args_retriever),
        headers={"content-type": "text/plain"},
    ),
}


#
# Records and record versions
#
class RDMRecordResourceConfig(RecordResourceConfig):
    """Record resource configuration."""

    blueprint_name = "records"
    url_prefix = "/records"

    routes = RecordResourceConfig.routes

    # PIDs
    routes["item-pids-reserve"] = "/<pid_value>/draft/pids/<pid_type>"

    request_view_args = {
        "pid_value": ma.fields.Str(),
        "pid_type": ma.fields.Str(),
    }

    request_read_args = {
        "style": ma.fields.Str(),
        "locale": ma.fields.Str(),
    }

    request_search_args = RDMSearchRequestArgsSchema

    response_handlers = record_serializers

    error_handlers = {
        StyleNotFoundError: create_error_handler(
            HTTPJSONException(
                code=400,
                description="Citation string style not found.",
            )
        ),
    }


#
# Record files
#
class RDMRecordFilesResourceConfig(FileResourceConfig):
    """Bibliographic record files resource config."""

    allow_upload = False
    blueprint_name = "record_files"
    url_prefix = "/records/<pid_value>"


#
# Draft files
#
class RDMDraftFilesResourceConfig(FileResourceConfig):
    """Bibliographic record files resource config."""

    blueprint_name = "draft_files"
    url_prefix = "/records/<pid_value>/draft"


#
# Parent Record Links
#
record_links_error_handlers = RecordResourceConfig.error_handlers.copy()


record_links_error_handlers.update(
    {
        LookupError: create_error_handler(
            HTTPJSONException(
                code=404,
                description="No secret link found with the given ID.",
            )
        ),
    }
)


class RDMParentRecordLinksResourceConfig(RecordResourceConfig):
    """User records resource configuration."""

    blueprint_name = "record_access"

    url_prefix = "/records/<pid_value>/access"

    routes = {
        "list": "/links",
        "item": "/links/<link_id>",
    }

    links_config = {}

    request_view_args = {
        "pid_value": ma.fields.Str(),
        "link_id": ma.fields.Str(),
    }

    response_handlers = {"application/json": ResponseHandler(JSONSerializer())}

    error_handlers = record_links_error_handlers
