# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C)      2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service."""

from invenio_drafts_resources.services.records.components import \
    DraftFilesComponent, PIDComponent
from invenio_drafts_resources.services.records.config import \
    RecordServiceConfig, SearchDraftsOptions, SearchOptions, \
    SearchVersionsOptions, is_draft, is_record
from invenio_records_resources.services import ConditionalLink, \
    FileServiceConfig, RecordLink
from invenio_records_resources.services.records.search import terms_filter

from ..external_pids import Providers
from ..records import RDMDraft, RDMRecord
from .components import AccessComponent, MetadataComponent, \
    ExternalPIDsComponent
from .permissions import RDMRecordPermissionPolicy
from .result_items import SecretLinkItem, SecretLinkList
from .schemas import RDMParentSchema, RDMRecordSchema
from .schemas.parent.access import SecretLink


#
# Search options
#
class RDMSearchOptions(SearchOptions):
    """Search options for record search."""

    facets_options = dict(
        aggs={
            'resource_type': {
                'terms': {'field': 'metadata.resource_type.type'},
                'aggs': {
                    'subtype': {
                        'terms': {'field': 'metadata.resource_type.subtype'},
                    }
                }
            },
            # 'access_right': {
            #     'terms': {'field': 'access.access_right'},
            # },
            # 'languages': {
            #     'terms': {'field': 'metadata.languages.id'},
            # },
        },
        post_filters={
            'subtype': terms_filter('metadata.resource_type.subtype'),
            'resource_type': terms_filter('metadata.resource_type.type'),
            # 'access_right': terms_filter('access.access_right'),
            # 'languages': terms_filter('metadata.languages.id'),
        }
    )


class RDMSearchDraftsOptions(SearchDraftsOptions):
    """Search options for drafts search."""

    facets_options = dict(
        aggs={
            'resource_type': {
                'terms': {'field': 'metadata.resource_type.type'},
                'aggs': {
                    'subtype': {
                        'terms': {'field': 'metadata.resource_type.subtype'},
                    }
                }
            },
            # 'access_right': {
            #     'terms': {'field': 'access.access_right'},
            # },
            # 'languages': {
            #     'terms': {'field': 'metadata.languages.id'},
            # },
            'is_published': {
                'terms': {'field': 'is_published'},
            },
        },
        post_filters={
            'subtype': terms_filter('metadata.resource_type.subtype'),
            'resource_type': terms_filter('metadata.resource_type.type'),
            # 'access_right': terms_filter('access.access_right'),
            # 'languages': terms_filter('metadata.languages.id'),
            'is_published': terms_filter('is_published'),
        }
    )


#
# Service configuration
#
class RDMRecordServiceConfig(RecordServiceConfig):
    """RDM record draft service config."""

    # Record and draft classes
    record_cls = RDMRecord
    draft_cls = RDMDraft

    # Schemas
    schema = RDMRecordSchema
    schema_parent = RDMParentSchema
    schema_secret_link = SecretLink

    # Permission policy
    permission_policy_cls = RDMRecordPermissionPolicy

    # Result classes
    link_result_item_cls = SecretLinkItem
    link_result_list_cls = SecretLinkList

    # Search configuration
    search = RDMSearchOptions
    search_drafts = RDMSearchDraftsOptions
    search_versions = SearchVersionsOptions

    # Components
    components = [
        MetadataComponent,
        AccessComponent,
        DraftFilesComponent,
        PIDComponent,
        ExternalPIDsComponent,
    ]

    # External PIDs providers
    external_pids_providers = Providers

    # Links
    links_item = {
        "self": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/records/{id}"),
            else_=RecordLink("{+api}/records/{id}/draft"),
        ),
        "self_html": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+ui}/records/{id}"),
            else_=RecordLink("{+ui}/uploads/{id}"),
        ),
        "files": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/records/{id}/files"),
            else_=RecordLink("{+api}/records/{id}/draft/files"),
        ),
        "latest": RecordLink("{+api}/records/{id}/versions/latest"),
        "latest_html": RecordLink("{+ui}/records/{id}/latest"),
        "publish": RecordLink(
            "{+api}/records/{id}/draft/actions/publish",
            when=is_draft
        ),
        "versions": RecordLink("{+api}/records/{id}/versions"),
        "access_links": RecordLink("{+api}/records/{id}/access/links"),
    }


class RDMFileRecordServiceConfig(FileServiceConfig):
    """Configuration for record files."""

    record_cls = RDMRecord
    permission_policy_cls = RDMRecordPermissionPolicy


class RDMFileDraftServiceConfig(FileServiceConfig):
    """Configuration for draft files."""

    record_cls = RDMDraft
    permission_policy_cls = RDMRecordPermissionPolicy
