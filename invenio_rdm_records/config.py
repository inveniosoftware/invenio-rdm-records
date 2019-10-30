# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University,
#                    Galter Health Sciences Library & Learning Center.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

from invenio_indexer.api import RecordIndexer
from invenio_records_files.api import Record
from invenio_records_permissions import record_create_permission_factory, \
    record_delete_permission_factory, record_list_permission_factory, \
    record_read_permission_factory, record_update_permission_factory
from invenio_records_permissions.api import RecordsSearch
from invenio_records_rest.facets import terms_filter


def _(x):
    """Identity function for string extraction."""
    return x


# Records REST API endpoints.

RECORDS_REST_ENDPOINTS = dict(
    recid=dict(
        pid_type='recid',
        pid_minter='recid',
        pid_fetcher='recid',
        default_endpoint_prefix=True,
        search_class=RecordsSearch,
        indexer_class=RecordIndexer,
        record_class=Record,
        search_index='records',
        search_type=None,
        record_serializers={
            'application/json': ('invenio_rdm_records.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('invenio_rdm_records.serializers'
                                 ':json_v1_search'),
        },
        record_loaders={
            'application/json': ('invenio_rdm_records.loaders'
                                 ':json_v1'),
        },
        list_route='/records/',
        item_route='/records/<pid(recid,'
                   'record_class="invenio_records_files.api.Record")'
                   ':pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        error_handlers=dict(),
        read_permission_factory_imp=record_read_permission_factory,
        list_permission_factory_imp=record_list_permission_factory,
        create_permission_factory_imp=record_create_permission_factory,
        update_permission_factory_imp=record_update_permission_factory,
        delete_permission_factory_imp=record_delete_permission_factory,
    ),
)
"""REST API for invenio_rdm_records."""

RECORDS_REST_FACETS = dict(
    records=dict(
        aggs=dict(
            keywords=dict(terms=dict(field='keywords'))
        ),
        post_filters=dict(
            keywords=terms_filter('keywords'),
        )
    )
)
"""Introduce searching facets."""


RECORDS_REST_SORT_OPTIONS = dict(
    records=dict(
        bestmatch=dict(
            title=_('Best match'),
            fields=['_score'],
            default_order='desc',
            order=1,
        ),
        mostrecent=dict(
            title=_('Most recent'),
            fields=['-_created'],
            default_order='asc',
            order=2,
        ),
    )
)
"""Setup sorting options."""


RECORDS_REST_DEFAULT_SORT = dict(
    records=dict(
        query='bestmatch',
        noquery='mostrecent',
    )
)
"""Set default sorting options."""


# Records Permissions

RECORDS_PERMISSIONS_RECORD_POLICY = (
    'invenio_rdm_records.permissions.RDMRecordPermissionPolicy'
)
"""PermissionPolicy used by permission factories above."""

# Files REST

# TODO: Change for record_read_files_permission_factory when files permissions
#       are ready
FILES_REST_PERMISSION_FACTORY = record_read_permission_factory
"""Set default files permission factory."""

# Records Files

RECORDS_FILES_REST_ENDPOINTS = {
    'RECORDS_REST_ENDPOINTS': {
        'recid': '/files',
    }
}
"""Set default files rest endpoints."""

RECORDS_UI_ENDPOINTS = {
    'recid': {
        'pid_type': 'recid',
        'route': '/records/<pid_value>',
        'template': 'records/record.html',
    },
}
"""Records UI for RDM Records."""

SEARCH_UI_JSTEMPLATE_RESULTS = 'templates/records/results.html'
"""Result list template."""

PIDSTORE_RECID_FIELD = 'recid'
