# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C)      2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service."""

from flask_babelex import lazy_gettext as _
from invenio_drafts_resources.services.records.components import \
    DraftFilesComponent, PIDComponent
from invenio_drafts_resources.services.records.config import \
    RecordServiceConfig, SearchDraftsOptions, SearchOptions, \
    SearchVersionsOptions, is_draft, is_record
from invenio_records_resources.services import ConditionalLink, \
    FileServiceConfig, RecordLink
from invenio_records_resources.services.files.links import FileLink
from invenio_records_resources.services.records.links import RecordLink
from invenio_records_resources.services.records.search import \
    nested_terms_filter, terms_filter

from ..records import RDMDraft, RDMRecord
from .components import AccessComponent, ExternalPIDsComponent, \
    MetadataComponent
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
            'access_status': {
                'terms': {'field': 'access.status'},
            },
            # 'languages': {
            #     'terms': {'field': 'metadata.languages.id'},
            # },
        },
        post_filters={
            'resource_type': nested_terms_filter(
                'metadata.resource_type.type',
                'metadata.resource_type.subtype',
                splitchar='::',
            ),
            'access_status': terms_filter('access.status'),
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
            'access_status': {
                'terms': {'field': 'access.status'},
            },
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
            'access_status': terms_filter('access.status'),
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

    # PIDs providers
    # PIDS-FIXME: setup default providers
    pids_providers = {}

    # Components
    components = [
        MetadataComponent,
        AccessComponent,
        DraftFilesComponent,
        # for the internal `pid` field
        PIDComponent,
        # for the `pids` field (external PIDs)
        # PIDS-FIXME: Re-enable when pids implementation is ready
        # ExternalPIDsComponent,
    ]

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
    permission_action_prefix = "draft_"
    permission_policy_cls = RDMRecordPermissionPolicy

    file_links_list = {
        "self": RecordLink("{+api}/records/{id}/draft/files"),
    }

    file_links_item = {
        "self": FileLink("{+api}/records/{id}/draft/files/{key}"),
        "content": FileLink("{+api}/records/{id}/draft/files/{key}/content"),
        "commit": FileLink("{+api}/records/{id}/draft/files/{key}/commit"),
    }
