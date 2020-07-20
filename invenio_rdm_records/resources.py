# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Resource."""

from invenio_records_resources.resources import RecordResource, \
    RecordResourceConfig
from invenio_records_resources.responses import RecordResponse
from invenio_records_resources.serializers import RecordJSONSerializer

from .marshmallow.json import BibliographicRecordSchemaV1


class BibliographicRecordResourceConfig(RecordResourceConfig):
    """Bibliographic Record resource config."""

    item_route = "/rdm-records/<pid_value>"
    list_route = "/rdm-records"
    response_handlers = {
        "application/json": RecordResponse(
            RecordJSONSerializer(schema=BibliographicRecordSchemaV1)
        )
    }


class BibliographicRecordResource(RecordResource):
    """Record resource."""

    default_config = BibliographicRecordResourceConfig
