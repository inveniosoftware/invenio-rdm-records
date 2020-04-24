# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

from invenio_indexer.api import RecordIndexer
from invenio_resources.controller import RecordController
from invenio_resources.resources import RecordResource, RecordResourceConfig
from invenio_records_files.api import Record
from invenio_records_permissions.api import RecordsSearch

record_config = RecordResourceConfig(
    list_route="/records/",
    item_route="/records/<pid(recid,"
    'record_class="invenio_records_files.api.Record")'
    ":pid_value>",
    item_serializers={
        "application/json": "invenio_rdm_records.serializers:json_v1",
    },
    list_serializers={
        "application/json": "invenio_rdm_records.serializers:json_v1"
    },
    item_loaders={"application/json": "invenio_rdm_records.loaders:json_v1"},
)

record_controller = RecordController(
    pid_type_name="recid",
    pid_minter_name="recid_v2",
    pid_fetcher_name="recid_v2",
    record_class=Record,
    search_class=RecordsSearch,
    indexer_class=RecordIndexer,
)

record_resource = RecordResource(
    config=record_config, controller=record_controller
)
