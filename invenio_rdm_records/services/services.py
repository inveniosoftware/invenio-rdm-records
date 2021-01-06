# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Service."""

from invenio_drafts_resources.services.records import RecordDraftService, \
    RecordDraftServiceConfig
from invenio_drafts_resources.services.records.components import \
    DraftFilesComponent, RelationsComponent
from invenio_records_resources.services.files.config import FileServiceConfig
from invenio_records_resources.services.files.service import RecordFileService
from invenio_records_resources.services.records.components import \
    MetadataComponent
from invenio_records_resources.services.records.search import terms_filter
from invenio_records_resources.services.records.service import RecordService

from ..records import BibliographicDraft, BibliographicRecord
from .components import AccessComponent, CommunitiesComponent, StatsComponent
from .permissions import RDMRecordPermissionPolicy
from .schemas import RDMRecordSchema


class BibliographicRecordServiceConfig(RecordDraftServiceConfig):
    """Bibliografic record draft service config."""

    # Record class
    record_cls = BibliographicRecord
    # Draft class
    draft_cls = BibliographicDraft

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
        CommunitiesComponent,
        StatsComponent,
    ]


class BibliographicRecordService(RecordDraftService):
    """Bibliographic record service."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_SERVICE_CONFIG"
    default_config = BibliographicRecordServiceConfig


class BibliographicUserRecordsServiceConfig(BibliographicRecordServiceConfig):
    """Bibliographic user records service configuration."""

    record_cls = BibliographicDraft


class BibliographicUserRecordsService(RecordService):
    """Bibliographic user records service."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_USER_RECORDS_SERVICE_CONFIG"
    default_config = BibliographicUserRecordsServiceConfig


#
# Record files
#
class BibliographicRecordFilesServiceConfig(
        BibliographicRecordServiceConfig, FileServiceConfig):
    """Bibliographic record files service configuration."""


class BibliographicRecordFilesService(RecordFileService):
    """Bibliographic record files service."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_RECORD_FILES_SERVICE_CONFIG"
    default_config = BibliographicRecordFilesServiceConfig


#
# Draft files
#
class BibliographicDraftFilesServiceConfig(
        BibliographicRecordServiceConfig, FileServiceConfig):
    """Bibliographic draft files service configuration."""

    record_cls = BibliographicDraft


class BibliographicDraftFilesService(RecordFileService):
    """Bibliographic draft files service."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_DRAFT_FILES_SERVICE_CONFIG"
    default_config = BibliographicDraftFilesServiceConfig
