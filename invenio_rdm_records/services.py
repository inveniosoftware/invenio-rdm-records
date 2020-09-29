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
    RelationsComponent
from invenio_records_resources.services.records.components import \
    AccessComponent, FilesComponent, MetadataComponent, PIDSComponent
from invenio_records_resources.services.records.search import terms_filter

from .components import CommunitiesComponent, StatsComponent
from .models import BibliographicRecord, BibliographicRecordDraft
from .permissions import RDMRecordPermissionPolicy
from .schemas import RDMRecordSchemaV1


class BibliographicRecordServiceConfig(RecordDraftServiceConfig):
    """Bibliografic record draft service config."""

    # Record class
    record_cls = BibliographicRecord
    # Draft class
    draft_cls = BibliographicRecordDraft

    schema = RDMRecordSchemaV1
    permission_policy_cls = RDMRecordPermissionPolicy

    search_facets_options = dict(
        aggs={
            'resource_type': {
                'terms': {'field': 'resource_type.type'},
                'aggs': {
                    'subtype': {
                        'terms': {'field': 'resource_type.subtype'},
                    }
                }
            },
            'access_right': {
                'terms': {'field': 'access_right'},
            }
        },
        post_filters={
            'subtype': terms_filter('resource_type.subtype'),
            'resource_type': terms_filter('resource_type.type'),
        }
    )

    components = [
        MetadataComponent,
        PIDSComponent,
        RelationsComponent,
        AccessComponent,
        FilesComponent,
        CommunitiesComponent,
        StatsComponent,
    ]


class BibliographicRecordService(RecordDraftService):
    """Bibliographic record service."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_SERVICE_CONFIG"
    default_config = BibliographicRecordServiceConfig
