# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources configuration."""

import marshmallow as ma
from flask_resources import HTTPJSONException, JSONSerializer, \
    ResponseHandler, create_error_handler
from invenio_drafts_resources.resources import RecordResourceConfig
from invenio_records_resources.resources.files import FileResourceConfig

from .serializers import UIJSONSerializer

#
# Links
#
# RecordLinks = LinksSchema.create(links={
#     "self": ItemLink(template='/api/records/{pid_value}'),
#     "self_html": ItemLink(template='/records/{pid_value}'),
#     "files": ItemLink(template='/api/records/{pid_value}/files'),
#     "versions": ItemLink(template='/api/records/{pid_value}/versions'),
#     "latest": ItemLink(template='/api/records/{pid_value}/versions/latest'),
#     "latest_html": ItemLink(template='/records/{pid_value}/latest'),
#     "access_links": ItemLink(
#         template='/api/records/{pid_value}/access/links', permission="manage"
#     ),
# })


# DraftLinks = LinksSchema.create(links={
#     "self": ItemLink(template="/api/records/{pid_value}/draft"),
#     "self_html": ItemLink(template="/uploads/{pid_value}"),
#     "files": ItemLink(template="/api/records/{pid_value}/draft/files"),
#     "versions": ItemLink(template='/api/records/{pid_value}/versions'),
#     "latest": ItemLink(template='/api/records/{pid_value}/versions/latest'),
#     "latest_html": ItemLink(template='/records/{pid_value}/latest'),
#     "access_links": ItemLink(
#         template='/api/records/{pid_value}/access/links', permission="manage"
#     ),
#     "publish": ItemLink(
#         template="/api/records/{pid_value}/draft/actions/publish",
#         permission="publish",
#     ),
# })


# SearchLinks = SearchLinksSchema.create(
#     template="/api/records{?params*}")


# SearchVersionsLinks = SearchVersionsLinksSchema.create(
#     template='/api/records/{pid_value}/versions{?params*}'
# )


# RecordVersionsLinks = LinksSchema.create(links={
#     "self": ItemLink(template='/api/records/{pid_value}'),
#     "self_html": ItemLink(template="/records/{pid_value}"),
# })


# UserSearchLinks = SearchLinksSchema.create(
#     template="/api/user/records{?params*}")


# RecordFileLinks = LinksSchema.create(links={
#     "self": FileItemLink(
#         template="/api/records/{pid_value}/files/{key}"),
#     "content": FileItemLink(
#         template="/api/records/{pid_value}/files/{key}/content"),
#     "commit": FileItemLink(
#         template="/api/records/{pid_value}/files/{key}/commit"),
# })


# DraftFileLinks = LinksSchema.create(links={
#     "self": FileItemLink(
#         template="/api/records/{pid_value}/draft/files/{key}"),
#     "content": FileItemLink(
#         template="/api/records/{pid_value}/draft/files/{key}/content"),
#     "commit": FileItemLink(
#         template="/api/records/{pid_value}/draft/files/{key}/commit"),
# })


# RecordListFilesLinks = LinksSchema.create(links={
#     "self": ItemLink(template="/api/records/{pid_value}/files")
# })


# DraftListFilesLinks = LinksSchema.create(links={
#     "self": ItemLink(template="/api/records/{pid_value}/draft/files")
# })


#
# Response handlers
#
record_serializers = {
    "application/json": ResponseHandler(JSONSerializer()),
    "application/vnd.inveniordm.v1+json": ResponseHandler(UIJSONSerializer())
}


#
# Records and record versions
#
class RDMRecordResourceConfig(RecordResourceConfig):
    """Record resource configuration."""

    blueprint_name = "records"
    url_prefix = "/records"

    routes = RecordResourceConfig.routes
    routes["item-files-import"] = "/<pid_value>/draft/actions/files-import"

    response_handlers = record_serializers


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


record_links_error_handlers.update({
    LookupError: create_error_handler(
        HTTPJSONException(
            code=404,
            description="No secret link found with the given ID.",
        )
    ),
})


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
        "link_id": ma.fields.Str()
    }

    response_handlers = {
        "application/json": ResponseHandler(JSONSerializer())
    }

    error_handlers = record_links_error_handlers


class RDMPIDProviderResourceConfig(RecordResourceConfig):
    """PID provider resource configuration."""

    blueprint_name = "reserve"

    url_prefix = "/records/<pid_value>/draft/pids"

    routes = {
        "item": "/<providers>"
    }

    request_view_args = {
        "provider": ma.fields.Str(),
        "pid_value": ma.fields.Str(),
    }

    response_handlers = {
        "application/json": ResponseHandler(JSONSerializer())
    }

    error_handlers = record_links_error_handlers
