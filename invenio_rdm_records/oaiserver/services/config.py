# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OAI-PMH service API configuration."""

from invenio_i18n import lazy_gettext as _
from invenio_oaiserver.models import OAISet
from invenio_records_resources.services import ServiceConfig
from invenio_records_resources.services.base import EndpointLink
from invenio_records_resources.services.records.links import pagination_endpoint_links
from sqlalchemy import asc, desc

from ..services.permissions import OAIPMHServerPermissionPolicy
from ..services.results import (
    OAIMetadataFormatItem,
    OAIMetadataFormatList,
    OAISetItem,
    OAISetList,
)
from .schema import OAIPMHMetadataFormat, OAIPMHSetSchema


class SearchOptions:
    """Search options."""

    sort_default = "created"
    sort_direction_default = "asc"

    sort_direction_options = {
        "asc": dict(
            title=_("Ascending"),
            fn=asc,
        ),
        "desc": dict(
            title=_("Descending"),
            fn=desc,
        ),
    }

    sort_options = {
        "name": dict(
            title=_("Name"),
            fields=["name"],
        ),
        "spec": dict(
            title=_("Spec"),
            fields=["spec"],
        ),
        "created": dict(
            title=_("Created"),
            fields=["created"],
        ),
        "updated": dict(
            title=_("Updated"),
            fields=["updated"],
        ),
    }
    pagination_options = {
        "default_results_per_page": 25,
    }


class OAIPMHServerServiceConfig(ServiceConfig):
    """Service factory configuration."""

    service_id = "oaipmh-server"

    # Common configuration
    permission_policy_cls = OAIPMHServerPermissionPolicy
    result_item_cls = OAISetItem
    result_list_cls = OAISetList

    metadata_format_result_item_cls = OAIMetadataFormatItem
    metadata_format_result_list_cls = OAIMetadataFormatList

    # Record specific configuration
    record_cls = OAISet

    # Search configuration
    search = SearchOptions

    # Service schema
    schema = OAIPMHSetSchema

    metadata_format_schema = OAIPMHMetadataFormat

    links_item = {
        "self": EndpointLink(
            "oaipmh-server.read",
            vars=lambda obj, vars_: vars_.update({"id": obj.id}),
            params=["id"],
        ),
        "oai-listrecords": EndpointLink(
            "invenio_oaiserver.response",
            vars=lambda obj, vars_: vars_.update(
                {
                    # querystring parameters
                    "args": {
                        "verb": "ListRecords",
                        "metadataPrefix": "oai_dc",
                        "set": obj.spec,
                    }
                }
            ),
        ),
        "oai-listidentifiers": EndpointLink(
            "invenio_oaiserver.response",
            vars=lambda obj, vars_: vars_.update(
                {
                    "args": {
                        "verb": "ListIdentifiers",
                        "metadataPrefix": "oai_dc",
                        "set": obj.spec,
                    }
                }
            ),
        ),
    }

    links_search = {
        **pagination_endpoint_links("oaipmh-server.search"),
        "oai-listsets": EndpointLink(
            "invenio_oaiserver.response",
            vars=lambda obj, vars_: vars_.update({"args": {"verb": "ListSets"}}),
        ),
        "oai-listrecords": EndpointLink(
            "invenio_oaiserver.response",
            vars=lambda obj, vars_: vars_.update(
                {
                    "args": {
                        "verb": "ListRecords",
                        "metadataPrefix": "oai_dc",
                    }
                }
            ),
        ),
        "oai-listidentifiers": EndpointLink(
            "invenio_oaiserver.response",
            vars=lambda obj, vars_: vars_.update(
                {
                    "args": {
                        "verb": "ListIdentifiers",
                        "metadataPrefix": "oai_dc",
                    }
                }
            ),
        ),
        "oai-identify": EndpointLink(
            "invenio_oaiserver.response",
            vars=lambda obj, vars_: vars_.update(
                {
                    "args": {
                        "verb": "Identify",
                    }
                }
            ),
        ),
    }
