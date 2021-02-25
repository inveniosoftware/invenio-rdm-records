# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service."""

from flask_babelex import lazy_gettext as _
from invenio_drafts_resources.services.records import RecordDraftServiceConfig
from invenio_drafts_resources.services.records.components import \
    DraftFilesComponent, PIDComponent
from invenio_records_resources.services.files.config import FileServiceConfig
from invenio_records_resources.services.records.search import terms_filter

from ..records import RDMDraft, RDMRecord
from .components import AccessComponent, MetadataComponent, \
    VersionSupportComponent
from .permissions import RDMRecordPermissionPolicy
from .schemas import RDMRecordSchema


class RDMRecordServiceConfig(RecordDraftServiceConfig):
    """RDM record draft service config."""

    # Record class
    record_cls = RDMRecord

    # Draft class
    draft_cls = RDMDraft

    schema = RDMRecordSchema

    permission_policy_cls = RDMRecordPermissionPolicy

    search_facets_options = dict(
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

    components = [
        MetadataComponent,
        AccessComponent,
        DraftFilesComponent,
        PIDComponent,
        VersionSupportComponent,
    ]


class RDMUserRecordsServiceConfig(RDMRecordServiceConfig):
    """RDM user records service configuration."""

    search_sort_default = 'bestmatch'
    search_sort_default_no_query = 'updated-desc'
    search_sort_options = {
        "bestmatch": dict(
            title=_('Best match'),
            fields=['_score'],  # ES defaults to desc on `_score` field
        ),
        "updated-desc": dict(
            title=_('Recently updated'),
            fields=['-updated'],
        ),
        "updated-asc": dict(
            title=_('Least recently updated'),
            fields=['updated'],
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

    search_facets_options = dict(
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
            'status': {
                'terms': {'field': 'status'},
            },
        },
        post_filters={
            'subtype': terms_filter('metadata.resource_type.subtype'),
            'resource_type': terms_filter('metadata.resource_type.type'),
            # 'access_right': terms_filter('access.access_right'),
            # 'languages': terms_filter('metadata.languages.id'),
            'status': terms_filter('status'),
        }
    )


#
# Record files
#
class RDMRecordFilesServiceConfig(RDMRecordServiceConfig, FileServiceConfig):
    """RDM record files service configuration."""


#
# Draft files
#
class RDMDraftFilesServiceConfig(
        RDMRecordServiceConfig, FileServiceConfig):
    """RDM draft files service configuration."""

    record_cls = RDMDraft
