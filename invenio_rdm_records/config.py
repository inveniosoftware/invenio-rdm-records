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
    record_read_files_permission_factory, record_read_permission_factory, \
    record_update_permission_factory
from invenio_records_permissions.api import RecordsSearch

RDM_RECORDS_DEFAULT_VALUE = 'foobar'
"""Default value for the application."""

RDM_RECORDS_BASE_TEMPLATE = 'invenio_rdm_records/base.html'
"""Default base template for the demo page."""

# Records REST API endpoints.

RECORDS_REST_ENDPOINTS = dict(
    recid=dict(
        pid_type='recid',
        pid_minter='recid',
        pid_fetcher='recid',
        search_class=RecordsSearch,
        indexer_class=RecordIndexer,
        record_class=Record,
        search_index=None,
        search_type=None,
        record_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('invenio_records_rest.serializers'
                                 ':json_v1_search'),
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

# Records Permissions

RECORDS_PERMISSIONS_RECORD_FACTORY = ('invenio_rdm_records.permissions:'
                                      'RDMRecordPermissionConfig')

# Files REST

FILES_REST_PERMISSION_FACTORY = record_read_files_permission_factory

# Records Files

RECORDS_FILES_REST_ENDPOINTS = {
    'RECORDS_REST_ENDPOINTS': {
        'recid': '/files',
    }
}

# TODO: UI Endpoints

# TODO: JSTemplate Results

# TODO: PIDStore RECID Field
