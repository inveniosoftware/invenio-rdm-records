# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2022 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2022 Universität Hamburg.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources configuration."""

import marshmallow as ma
from citeproc_styles import StyleNotFoundError
from flask_babelex import lazy_gettext as _
from flask_resources import (
    HTTPJSONException,
    JSONDeserializer,
    JSONSerializer,
    RequestBodyParser,
    ResourceConfig,
    ResponseHandler,
    create_error_handler,
    resource_requestctx,
)
from invenio_drafts_resources.resources import RecordResourceConfig
from invenio_records.systemfields.relations import InvalidRelationValue
from invenio_records_resources.resources.files import FileResourceConfig

from ..services.errors import (
    ReviewExistsError,
    ReviewInconsistentAccessRestrictions,
    ReviewNotFoundError,
    ReviewStateError,
    ValidationErrorWithMessageAsList,
)
from .args import RDMSearchRequestArgsSchema
from .deserializers import ROCrateJSONDeserializer
from .deserializers.errors import DeserializerError
from .errors import HTTPJSONValidationWithMessageAsListException
from .serializers import (
    CSLJSONSerializer,
    DataCite43JSONSerializer,
    DataCite43XMLSerializer,
    DublinCoreXMLSerializer,
    StringCitationSerializer,
    UIJSONSerializer,
)


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
    "application/vnd.citationstyles.csl+json": ResponseHandler(CSLJSONSerializer()),
    "application/vnd.datacite.datacite+json": ResponseHandler(
        DataCite43JSONSerializer()
    ),
    "application/vnd.datacite.datacite+xml": ResponseHandler(DataCite43XMLSerializer()),
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
    routes["item-pids-reserve"] = "/<pid_value>/draft/pids/<scheme>"
    # Review
    routes["item-review"] = "/<pid_value>/draft/review"
    routes["item-actions-review"] = "/<pid_value>/draft/actions/submit-review"
    # Community records
    routes["community-records"] = "/communities/<pid_value>/records"

    request_view_args = {
        "pid_value": ma.fields.Str(),
        "scheme": ma.fields.Str(),
    }

    request_read_args = {
        "style": ma.fields.Str(),
        "locale": ma.fields.Str(),
    }

    request_body_parsers = {
        "application/json": RequestBodyParser(JSONDeserializer()),
        'application/ld+json;profile="https://w3id.org/ro/crate/1.1"': RequestBodyParser(
            ROCrateJSONDeserializer()
        ),
    }

    request_search_args = RDMSearchRequestArgsSchema

    response_handlers = record_serializers

    error_handlers = {
        DeserializerError: create_error_handler(
            lambda exc: HTTPJSONException(
                code=400,
                description=exc.args[0],
            )
        ),
        StyleNotFoundError: create_error_handler(
            HTTPJSONException(
                code=400,
                description=_("Citation string style not found."),
            )
        ),
        ReviewNotFoundError: create_error_handler(
            HTTPJSONException(
                code=404,
                description=_("Review for draft not found"),
            )
        ),
        ReviewStateError: create_error_handler(
            lambda e: HTTPJSONException(
                code=400,
                description=str(e),
            )
        ),
        ReviewExistsError: create_error_handler(
            lambda e: HTTPJSONException(
                code=400,
                description=str(e),
            )
        ),
        InvalidRelationValue: create_error_handler(
            lambda exc: HTTPJSONException(
                code=400,
                description=exc.args[0],
            )
        ),
        ReviewInconsistentAccessRestrictions: create_error_handler(
            lambda exc: HTTPJSONException(
                code=400,
                description=exc.args[0],
            )
        ),
        ValidationErrorWithMessageAsList: create_error_handler(
            lambda e: HTTPJSONValidationWithMessageAsListException(e)
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


class IIIFResourceConfig(ResourceConfig):
    """IIIF resource configuration."""

    blueprint_name = "iiif"

    url_prefix = "/iiif"

    routes = {
        "manifest": "/<uuid>/manifest",
        "sequence": "/<uuid>/sequence/default",
        "canvas": "/<uuid>/canvas/<file_name>",
        "image_base": "/<uuid>",
        "image_info": "/<uuid>/info.json",
        "image_api": "/<uuid>/<region>/<size>/<rotation>/<quality>.<image_format>",
    }

    request_view_args = {
        "uuid": ma.fields.Str(),
        "file_name": ma.fields.Str(),
        "region": ma.fields.Str(),
        "size": ma.fields.Str(),
        "rotation": ma.fields.Str(),
        "quality": ma.fields.Str(),
        "image_format": ma.fields.Str(),
    }

    request_read_args = {
        "dl": ma.fields.Str(),
    }

    request_headers = {
        "If-Modified-Since": ma.fields.DateTime(),
    }

    response_handler = {"application/json": ResponseHandler(JSONSerializer())}

    supported_formats = {
        "gif": "image/gif",
        "jp2": "image/jp2",
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "pdf": "application/pdf",
        "png": "image/png",
        "tif": "image/tiff",
        "tiff": "image/tiff",
    }
