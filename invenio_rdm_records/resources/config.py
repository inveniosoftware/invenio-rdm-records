# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2022 Universität Hamburg.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resources configuration."""

from copy import deepcopy

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
    CommunityRequiredError,
    GrantExistsError,
    InvalidAccessRestrictions,
    RecordDeletedException,
    RecordSubmissionClosedCommunityError,
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
    CSVRecordSerializer,
    DataCite43JSONSerializer,
    DataCite43XMLSerializer,
    DCATSerializer,
    DublinCoreXMLSerializer,
    FAIRSignpostingProfileLvl2Serializer,
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
    "application/vnd.inveniordm.v1.full+csv": ResponseHandler(CSVRecordSerializer()),
    "application/vnd.inveniordm.v1.simple+csv": ResponseHandler(
        CSVRecordSerializer(
            csv_included_fields=[
                "id",
                "created",
                "pids.doi.identifier",
                "metadata.title",
                "metadata.description",
                "metadata.resource_type.title.en",
                "metadata.publication_date",
                "metadata.creators.person_or_org.type",
                "metadata.creators.person_or_org.name",
                "metadata.rights.id",
            ],
            collapse_lists=True,
        )
    ),
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
    "application/linkset+json": ResponseHandler(FAIRSignpostingProfileLvl2Serializer()),
}

error_handlers = {
    **ErrorHandlersMixin.error_handlers,
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
    RecordSubmissionClosedCommunityError: create_error_handler(
        lambda e: HTTPJSONException(
            code=403,
            description=e.description,
        )
    ),
    CommunityRequiredError: create_error_handler(
        HTTPJSONException(
            code=400,
            description=_("Cannot publish without selecting a community."),
        )
    ),
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
    routes["item-revision-list"] = "/<pid_value>/revisions"

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

    error_handlers = FromConfig(
        "RDM_RECORDS_ERROR_HANDLERS",
        default=error_handlers,
    )


#
# Record files
#
class RDMRecordFilesResourceConfig(FileResourceConfig, ConfiguratorMixin):
    """Bibliographic record files resource config."""

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

    blueprint_name = "draft_files"
    url_prefix = "/records/<pid_value>/draft"

    response_handlers = {
        "application/vnd.inveniordm.v1+json": FileResourceConfig.response_handlers[
            "application/json"
        ],
        **FileResourceConfig.response_handlers,
    }


#
# Record Media files
#
class RDMRecordMediaFilesResourceConfig(FileResourceConfig, ConfiguratorMixin):
    """Bibliographic record files resource config."""

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

    response_handlers = {
        "application/vnd.inveniordm.v1+json": FileResourceConfig.response_handlers[
            "application/json"
        ],
        **FileResourceConfig.response_handlers,
    }


#
# Draft Media files
#
class RDMDraftMediaFilesResourceConfig(FileResourceConfig, ConfiguratorMixin):
    """Bibliographic record files resource config."""

    blueprint_name = "draft_media_files"
    url_prefix = "/records/<pid_value>/draft"

    routes = {
        "list": "/media-files",
        "item": "/media-files/<key>",
        "item-content": "/media-files/<key>/content",
        "item-commit": "/media-files/<key>/commit",
        "list-archive": "/media-files-archive",
    }

    response_handlers = {
        "application/vnd.inveniordm.v1+json": FileResourceConfig.response_handlers[
            "application/json"
        ],
        **FileResourceConfig.response_handlers,
    }


#
# Parent Record Links
#
record_links_error_handlers = {
    **deepcopy(RecordResourceConfig.error_handlers),
    LookupError: create_error_handler(
        HTTPJSONException(
            code=404,
            description=_("No secret link found with the given ID."),
        )
    ),
}

grants_error_handlers = {
    **deepcopy(RecordResourceConfig.error_handlers),
    LookupError: create_error_handler(
        HTTPJSONException(code=404, description=_("No grant found with the given ID."))
    ),
    GrantExistsError: create_error_handler(
        lambda e: HTTPJSONException(
            code=400,
            description=e.description,
        )
    ),
}

user_access_error_handlers = {
    **deepcopy(RecordResourceConfig.error_handlers),
    LookupError: create_error_handler(
        HTTPJSONException(code=404, description=_("No grant found by given user id."))
    ),
}

group_access_error_handlers = {
    **deepcopy(RecordResourceConfig.error_handlers),
    LookupError: create_error_handler(
        HTTPJSONException(code=404, description=_("No grant found by given group id."))
    ),
}


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
        "application/vnd.inveniordm.v1+json": RecordResourceConfig.response_handlers[
            "application/json"
        ],
        **RecordResourceConfig.response_handlers,
    }

    error_handlers = record_links_error_handlers


class RDMParentGrantsResourceConfig(RecordResourceConfig, ConfiguratorMixin):
    """Record grants resource configuration."""

    blueprint_name = "record_grants"

    url_prefix = "/records/<pid_value>/access"

    routes = {
        "list": "/grants",
        "item": "/grants/<grant_id>",
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
        "application/vnd.inveniordm.v1+json": RecordResourceConfig.response_handlers[
            "application/json"
        ],
        **RecordResourceConfig.response_handlers,
    }

    error_handlers = grants_error_handlers


class RDMGrantUserAccessResourceConfig(RecordResourceConfig, ConfiguratorMixin):
    """Record grants user access resource configuration."""

    blueprint_name = "record_user_access"

    url_prefix = "/records/<pid_value>/access"

    routes = {
        "item": "/users/<subject_id>",
        "list": "/users",
    }

    links_config = {}

    request_view_args = {
        "pid_value": ma.fields.Str(),
        "subject_id": ma.fields.Str(),  # user id
    }

    grant_subject_type = "user"

    response_handlers = {
        "application/vnd.inveniordm.v1+json": RecordResourceConfig.response_handlers[
            "application/json"
        ],
        **deepcopy(RecordResourceConfig.response_handlers),
    }

    error_handlers = user_access_error_handlers


class RDMGrantGroupAccessResourceConfig(RecordResourceConfig, ConfiguratorMixin):
    """Record grants group access resource configuration."""

    blueprint_name = "record_group_access"

    url_prefix = "/records/<pid_value>/access"

    routes = {
        "item": "/groups/<subject_id>",
        "list": "/groups",
    }

    links_config = {}

    request_view_args = {
        "pid_value": ma.fields.Str(),
        "subject_id": ma.fields.Str(),  # group id
    }

    grant_subject_type = "role"

    response_handlers = {
        "application/vnd.inveniordm.v1+json": RecordResourceConfig.response_handlers[
            "application/json"
        ],
        **deepcopy(RecordResourceConfig.response_handlers),
    }

    error_handlers = group_access_error_handlers


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

    blueprint_name = "record_communities"
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

    blueprint_name = "record_requests"
    url_prefix = "/records"
    routes = {"list": "/<record_pid>/requests"}

    request_search_args = RequestSearchRequestArgsSchema

    request_view_args = {
        "record_pid": ma.fields.Str(),
    }

    request_extra_args = {
        "expand": ma.fields.Boolean(),
    }

    response_handlers = {
        "application/vnd.inveniordm.v1+json": ResourceConfig.response_handlers[
            "application/json"
        ],
        **ResourceConfig.response_handlers,
    }
