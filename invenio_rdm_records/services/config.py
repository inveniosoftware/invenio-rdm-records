# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service."""

from invenio_drafts_resources.services.records import RecordDraftServiceConfig
from invenio_drafts_resources.services.records.components import \
    DraftFilesComponent, RelationsComponent
from invenio_records_resources.services.files.config import FileServiceConfig
from invenio_records_resources.services.records.components import \
    MetadataComponent
from invenio_records_resources.services.records.search import terms_filter

from ..records import RDMDraft, RDMRecord
from .components import AccessComponent
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
            'access_right': {
                'terms': {'field': 'access.access_right'},
            },
            'languages': {
                'terms': {'field': 'metadata.languages.id'},
            }
        },
        post_filters={
            'subtype': terms_filter('metadata.resource_type.subtype'),
            'resource_type': terms_filter('metadata.resource_type.type'),
            'access_right': terms_filter('access.access_right'),
            'languages': terms_filter('metadata.languages.id'),
        }
    )

    components = [
        MetadataComponent,
        RelationsComponent,
        AccessComponent,
        DraftFilesComponent,
    ]


class RDMUserRecordsServiceConfig(RDMRecordServiceConfig):
    """RDM user records service configuration."""

    record_cls = RDMDraft


#
# Record files
#
class RDMRecordFilesServiceConfig(
        RDMRecordServiceConfig, FileServiceConfig):
    """RDM record files service configuration."""


#
# Draft files
#
class RDMDraftFilesServiceConfig(
        RDMRecordServiceConfig, FileServiceConfig):
    """RDM draft files service configuration."""

    record_cls = RDMDraft
