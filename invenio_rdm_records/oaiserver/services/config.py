# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""OAI-PMH service API configuration."""

from flask_babelex import gettext as _
from invenio_indexer.api import RecordIndexer
from invenio_oaiserver.models import OAISet
from invenio_records_resources.services import ServiceConfig
from invenio_records_resources.services.base import Link
from invenio_records_resources.services.records.links import pagination_links
from invenio_records_resources.services.records.params import (
    FacetsParam,
    PaginationParam,
    QueryParser,
    QueryStrParam,
    SortParam,
)
from invenio_search import RecordsSearchV2
from marshmallow import Schema, fields, validate

from invenio_rdm_records.oaiserver.services.links import OAIPMHSetLink
from invenio_rdm_records.oaiserver.services.permissions import (
    OAIPMHServerPermissionPolicy,
)
from invenio_rdm_records.oaiserver.services.results import (
    OAISetItem,
    OAISetList,
)


class SearchOptions:
    """Search options."""

    search_cls = RecordsSearchV2
    query_parser_cls = QueryParser
    suggest_parser_cls = None
    sort_default = 'bestmatch'
    sort_default_no_query = 'newest'
    sort_options = {
        "bestmatch": dict(
            title=_('Best match'),
            fields=['_score'],  # ES defaults to desc on `_score` field
        ),
        "newest": dict(
            title=_('Newest'),
            fields=['-created'],
        ),
        "oldest": dict(
            title=_('Oldest'),
            fields=['created'],
        ),
    }
    facets = {}
    pagination_options = {
        "default_results_per_page": 25,
        "default_max_results": 10000,
    }
    params_interpreters_cls = [
        QueryStrParam,
        PaginationParam,
        SortParam,
        FacetsParam,
    ]


class OAIPMHSetSchema(Schema):
    """Marshmallow schema for OAI-PMH set."""

    description = fields.Str(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    search_pattern = fields.Str(required=True, validate=validate.Length(min=1))
    spec = fields.Str(required=True, validate=validate.Length(min=1))
    created = fields.DateTime(read_only=True)
    updated = fields.DateTime(read_only=True)
    id = fields.Int(read_only=True)


class OAIPMHSetUpdateSchema(Schema):
    """Marshmallow schema for OAI-PMH set update request."""

    description = fields.Str(validate=validate.Length(min=1))
    name = fields.Str(validate=validate.Length(min=1))
    search_pattern = fields.Str(validate=validate.Length(min=1))


class OAIPMHServerServiceConfig(ServiceConfig):
    """Service factory configuration."""

    # Common configuration
    permission_policy_cls = OAIPMHServerPermissionPolicy
    result_item_cls = OAISetItem
    result_list_cls = OAISetList

    # Record specific configuration
    record_cls = OAISet
    indexer_cls = None
    index_dumper = None

    # Search configuration
    search = SearchOptions

    # Service schema
    schema = OAIPMHSetSchema
    update_schema = OAIPMHSetUpdateSchema

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
