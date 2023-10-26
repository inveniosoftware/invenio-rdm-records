# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2022 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2022 Universität Hamburg.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources configuration."""

import marshmallow as ma
from citeproc_styles import StyleNotFoundError
from flask_resources import (
    JSONDeserializer,
    JSONSerializer,
    RequestBodyParser,
    ResourceConfig,
    ResponseHandler,
    create_error_handler,
    resource_requestctx,
)
from invenio_communities.communities.resources import CommunityResourceConfig
from invenio_communities.communities.resources.config import community_error_handlers
from invenio_drafts_resources.resources import RecordResourceConfig
from invenio_i18n import lazy_gettext as _
from invenio_records.systemfields.relations import InvalidRelationValue
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.files import FileResourceConfig
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_records_resources.services.base.config import ConfiguratorMixin, FromConfig
from invenio_requests.resources.requests.config import RequestSearchRequestArgsSchema

from ..services.errors import (
    AccessRequestExistsError,
    InvalidAccessRestrictions,
    RecordDeletedException,
    ReviewExistsError,
    ReviewNotFoundError,
    ReviewStateError,
    ValidationErrorWithMessageAsList,
)
from .args import RDMSearchRequestArgsSchema
from .deserializers import ROCrateJSONDeserializer
from .deserializers.errors import DeserializerError
from .errors import HTTPJSONException, HTTPJSONValidationWithMessageAsListException
from .serializers import (
    BibtexSerializer,
    CSLJSONSerializer,
    DataCite43JSONSerializer,
    DataCite43XMLSerializer,
    DCATSerializer,
    DublinCoreXMLSerializer,
    GeoJSONSerializer,
    MARCXMLSerializer,
    SchemaorgJSONLDSerializer,
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
def _bibliography_headers(obj_or_list, code, many=False):
    """Override content type for 'text/x-bibliography'."""
    _etag_headers = etag_headers(obj_or_list, code, many=False)
    _etag_headers["content-type"] = "text/plain"
    return _etag_headers


record_serializers = {
    "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
    "application/ld+json": ResponseHandler(SchemaorgJSONLDSerializer()),
    "application/marcxml+xml": ResponseHandler(
        MARCXMLSerializer(), headers=etag_headers
    ),
    "application/vnd.inveniordm.v1+json": ResponseHandler(
        UIJSONSerializer(), headers=etag_headers
    ),
    "application/vnd.citationstyles.csl+json": ResponseHandler(
        CSLJSONSerializer(), headers=etag_headers
    ),
    "application/vnd.datacite.datacite+json": ResponseHandler(
        DataCite43JSONSerializer(), headers=etag_headers
    ),
    "application/vnd.geo+json": ResponseHandler(
        GeoJSONSerializer(), headers=etag_headers
    ),
    "application/vnd.datacite.datacite+xml": ResponseHandler(
        DataCite43XMLSerializer(), headers=etag_headers
    ),
    "application/x-dc+xml": ResponseHandler(
        DublinCoreXMLSerializer(), headers=etag_headers
    ),
    "text/x-bibliography": ResponseHandler(
        StringCitationSerializer(url_args_retriever=csl_url_args_retriever),
        headers=_bibliography_headers,
    ),
    "application/x-bibtex": ResponseHandler(BibtexSerializer(), headers=etag_headers),
    "application/dcat+xml": ResponseHandler(DCATSerializer(), headers=etag_headers),
}


#
# Records and record versions
#
class RDMRecordResourceConfig(RecordResourceConfig, ConfiguratorMixin):
    """Record resource configuration."""

    blueprint_name = "records"
    url_prefix = "/records"

    routes = RecordResourceConfig.routes

    # PIDs
    routes["item-pids-reserve"] = "/<pid_value>/draft/pids/<scheme>"
    # Review
    routes["item-review"] = "/<pid_value>/draft/review"
    routes["item-actions-review"] = "/<pid_value>/draft/actions/submit-review"
    # Access requests
    routes["record-access-request"] = "/<pid_value>/access/request"
    routes["access-request-settings"] = "/<pid_value>/access"
    routes["delete-record"] = "/<pid_value>/delete"
    routes["restore-record"] = "/<pid_value>/restore"
    routes["set-record-quota"] = "/<pid_value>/quota"
    routes["set-user-quota"] = "/users/<pid_value>/quota"

    request_view_args = {
        "pid_value": ma.fields.Str(),
        "scheme": ma.fields.Str(),
    }

    request_read_args = {
        "style": ma.fields.Str(),
        "locale": ma.fields.Str(),
        "include_deleted": ma.fields.Bool(),
    }

    request_body_parsers = {
        "application/json": RequestBodyParser(JSONDeserializer()),
        'application/ld+json;profile="https://w3id.org/ro/crate/1.1"': RequestBodyParser(
            ROCrateJSONDeserializer()
        ),
    }

    request_search_args = FromConfig(
        "RDM_SEARCH_ARGS_SCHEMA", default=RDMSearchRequestArgsSchema
    )

    response_handlers = FromConfig(
        "RDM_RECORDS_SERIALIZERS",
        default=record_serializers,
    )

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
        InvalidAccessRestrictions: create_error_handler(
            lambda exc: HTTPJSONException(
                code=400,
                description=exc.args[0],
            )
        ),
        ValidationErrorWithMessageAsList: create_error_handler(
            lambda e: HTTPJSONValidationWithMessageAsListException(e)
        ),
        AccessRequestExistsError: create_error_handler(
            lambda e: HTTPJSONException(
                code=400,
                description=e.description,
            )
        ),
        RecordDeletedException: create_error_handler(
            lambda e: (
                HTTPJSONException(code=404, description=_("Record not found"))
                if not e.record.tombstone.is_visible
                else HTTPJSONException(
                    code=410,
                    description=_("Record deleted"),
                    tombstone=e.record.tombstone.dump(),
                )
            )
        ),
    }


#
# Record files
#
class RDMRecordFilesResourceConfig(FileResourceConfig, ConfiguratorMixin):
    """Bibliographic record files resource config."""

    allow_upload = False
    allow_archive_download = FromConfig("RDM_ARCHIVE_DOWNLOAD_ENABLED", True)
    blueprint_name = "record_files"
    url_prefix = "/records/<pid_value>"

    error_handlers = {
        **ErrorHandlersMixin.error_handlers,
        RecordDeletedException: create_error_handler(
            lambda e: (
                HTTPJSONException(code=404, description=_("Record not found"))
                if not e.record.tombstone.is_visible
                else HTTPJSONException(
                    code=410,
                    description=_("Record deleted"),
                    tombstone=e.record.tombstone.dump(),
                )
            )
        ),
    }


#
# Draft files
#
class RDMDraftFilesResourceConfig(FileResourceConfig, ConfiguratorMixin):
    """Bibliographic record files resource config."""

    allow_archive_download = FromConfig("RDM_ARCHIVE_DOWNLOAD_ENABLED", True)
    blueprint_name = "draft_files"
    url_prefix = "/records/<pid_value>/draft"


class RDMRecordMediaFilesResourceConfig(FileResourceConfig, ConfiguratorMixin):
    """Bibliographic record files resource config."""

    allow_upload = False
    allow_archive_download = FromConfig("RDM_ARCHIVE_DOWNLOAD_ENABLED", True)
    blueprint_name = "record_media_files"
    url_prefix = "/records/<pid_value>"
    routes = {
        "list": "/media-files",
        "item": "/media-files/<key>",
        "item-content": "/media-files/<key>/content",
        "item-commit": "/media-files/<key>/commit",
        "list-archive": "/media-files-archive",
    }

    error_handlers = {
        **ErrorHandlersMixin.error_handlers,
        RecordDeletedException: create_error_handler(
            lambda e: (
                HTTPJSONException(code=404, description=_("Record not found"))
                if not e.record.tombstone.is_visible
                else HTTPJSONException(
                    code=410,
                    description=_("Record deleted"),
                    tombstone=e.record.tombstone.dump(),
                )
            )
        ),
    }


#
# Draft files
#
class RDMDraftMediaFilesResourceConfig(FileResourceConfig, ConfiguratorMixin):
    """Bibliographic record files resource config."""

    allow_archive_download = FromConfig("RDM_ARCHIVE_DOWNLOAD_ENABLED", True)
    blueprint_name = "draft_media_files"
    url_prefix = "/records/<pid_value>/draft"

    routes = {
        "list": "/media-files",
        "item": "/media-files/<key>",
        "item-content": "/media-files/<key>/content",
        "item-commit": "/media-files/<key>/commit",
        "list-archive": "/media-files-archive",
    }


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

grants_error_handlers = RecordResourceConfig.error_handlers.copy()

grants_error_handlers.update(
    {
        LookupError: create_error_handler(
            HTTPJSONException(code=404, description="No grant found with the given ID.")
        )
    }
)


#
# Parent Record Links
#
class RDMParentRecordLinksResourceConfig(RecordResourceConfig, ConfiguratorMixin):
    """User records resource configuration."""

    blueprint_name = "record_links"

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

    response_handlers = {
        "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers)
    }

    error_handlers = record_links_error_handlers


class RDMParentGrantsResourceConfig(RecordResourceConfig, ConfiguratorMixin):
    """Record grants resource configuration."""

    blueprint_name = "record_grants"

    url_prefix = "/records/<pid_value>/access"

    routes = {
        "list": "/users",
        "item": "/users/<grant_id>",
    }

    links_config = {}

    # NOTE: the `grant_id` is currently the index in the list of `parent.access.grants`
    #       which should only change when the data model changes, and should thus
    #       be good enough for our purposes
    request_view_args = {
        "pid_value": ma.fields.Str(),
        "grant_id": ma.fields.Int(),
    }
    request_extra_args = {"expand": ma.fields.Bool()}

    response_handlers = {
        "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers)
    }

    error_handlers = grants_error_handlers


#
# Community's records
#
class RDMCommunityRecordsResourceConfig(RecordResourceConfig, ConfiguratorMixin):
    """Community's records resource config."""

    blueprint_name = "community-records"
    url_prefix = "/communities"
    routes = {"list": "/<pid_value>/records"}

    response_handlers = FromConfig(
        "RDM_RECORDS_SERIALIZERS",
        default=record_serializers,
    )


class RDMRecordCommunitiesResourceConfig(CommunityResourceConfig, ConfiguratorMixin):
    """Record communities resource config."""

    blueprint_name = "records-community"
    url_prefix = "/records"
    routes = {
        "list": "/<pid_value>/communities",
        "suggestions": "/<pid_value>/communities-suggestions",
    }

    request_extra_args = {
        "expand": ma.fields.Boolean(),
        "membership": ma.fields.Boolean(),
    }

    error_handlers = community_error_handlers


class RDMRecordRequestsResourceConfig(ResourceConfig, ConfiguratorMixin):
    """Record communities resource config."""

    blueprint_name = "records-requests"
    url_prefix = "/records"
    routes = {"list": "/<record_pid>/requests"}

    request_search_args = RequestSearchRequestArgsSchema

    request_view_args = {
        "record_pid": ma.fields.Str(),
    }

    request_extra_args = {
        "expand": ma.fields.Boolean(),
    }


#
# IIIF
#
class IIIFResourceConfig(ResourceConfig, ConfiguratorMixin):
    """IIIF resource configuration."""

    blueprint_name = "iiif"

    url_prefix = "/iiif"

    routes = {
        "manifest": "/<path:uuid>/manifest",
        "sequence": "/<path:uuid>/sequence/default",
        "canvas": "/<path:uuid>/canvas/<path:file_name>",
        "image_base": "/<path:uuid>",
        "image_info": "/<path:uuid>/info.json",
        "image_api": "/<path:uuid>/<region>/<size>/<rotation>/<quality>.<image_format>",
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
