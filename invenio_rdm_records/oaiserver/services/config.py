# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OAI-PMH service API configuration."""

from flask_babelex import gettext as _
from invenio_oaiserver.models import OAISet
from invenio_records_resources.services import ServiceConfig
from invenio_records_resources.services.base import Link
from invenio_records_resources.services.records.links import pagination_links
from marshmallow import Schema, fields, validate
from marshmallow_utils.fields import SanitizedUnicode
from sqlalchemy import asc, desc

from ..services.links import OAIPMHSetLink
from ..services.permissions import OAIPMHServerPermissionPolicy
from ..services.results import OAIMetadataFormatItem, OAIMetadataFormatList, \
    OAISetItem, OAISetList


class SearchOptions:
    """Search options."""

    sort_default = 'created'
    sort_direction_default = 'asc'

    sort_direction_options = {
        "asc": dict(
            title=_('Ascending'),
            fn=asc,
        ),
        "desc": dict(
            title=_('Descending'),
            fn=desc,
        ),
    }

    sort_options = {
        "name": dict(
            title=_('Name'),
            fields=['name'],
        ),
        "spec": dict(
            title=_('Spec'),
            fields=['spec'],
        ),
        "created": dict(
            title=_('Created'),
            fields=['created'],
        ),
        "updated": dict(
            title=_('Updated'),
            fields=['updated'],
        ),
    }
    pagination_options = {
        "default_results_per_page": 25,
    }


class OAIPMHMetadataFormat(Schema):
    """Marshmallow schema for OAI-PMH metadata format."""

    id = fields.Str(metadata={'read_only': True})
    schema = fields.URL(metadata={'read_only': True})
    namespace = fields.URL(metadata={'read_only': True})


class OAIPMHSetSchema(Schema):
    """Marshmallow schema for OAI-PMH set."""

    description = SanitizedUnicode(load_default=None, dump_default=None)
    name = SanitizedUnicode(required=True, validate=validate.Length(min=1))
    search_pattern = SanitizedUnicode(required=True)
    spec = SanitizedUnicode(required=True, validate=validate.Length(min=1))
    created = fields.DateTime(metadata={'read_only': True})
    updated = fields.DateTime(metadata={'read_only': True})
    id = fields.Int(metadata={'read_only': True})


class OAIPMHSetUpdateSchema(Schema):
    """Marshmallow schema for OAI-PMH set update request."""

    description = SanitizedUnicode(load_default=None)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    search_pattern = fields.Str(required=True)


class OAIPMHServerServiceConfig(ServiceConfig):
    """Service factory configuration."""

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
    update_schema = OAIPMHSetUpdateSchema

    metadata_format_schema = OAIPMHMetadataFormat

    links_item = {
        "self": OAIPMHSetLink("{+api}/oaipmh/sets/{id}"),
        "oai-listrecords": OAIPMHSetLink(
            "{+ui}/oai2d?verb=ListRecords&metadataPrefix=oai_dc&set={spec}"
        ),
        "oai-listidentifiers": OAIPMHSetLink(
            "{+ui}/oai2d?verb=ListIdentifiers&metadataPrefix=oai_dc&set={spec}"
        ),
    }

    links_search = {
        **pagination_links("{+api}/oaipmh/sets{?args*}"),
        "oai-listsets": Link("{+ui}/oai2d?verb=ListSets"),
        "oai-listrecords": Link(
            "{+ui}/oai2d?verb=ListRecords&metadataPrefix=oai_dc"
        ),
        "oai-listidentifiers": Link(
            "{+ui}/oai2d?verb=ListIdentifiers&metadataPrefix=oai_dc"
        ),
        "oai-identify": Link("{+ui}/oai2d?verb=Identify"),
    }

    # Service components
    components = [
        # MetadataComponent,
    ]
