# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Resource."""

from invenio_drafts_resources.resources import DraftActionResource, \
    DraftActionResourceConfig, DraftResource, DraftResourceConfig, \
    RecordResource, RecordResourceConfig
from invenio_records_resources.resources import RecordResponse
from marshmallow.exceptions import ValidationError

from .errors import handle_validation_error
from .schemas_links import BibliographicDraftLinksSchemaV1, \
    BibliographicRecordLinksSchemaV1, \
    BibliographicUserRecordsSearchLinksSchemaV1
from .serializers import UIJSONSerializer


class BibliographicRecordResourceConfig(RecordResourceConfig):
    """Bibliographic record resource configuration."""

    links_config = {
        **RecordResourceConfig.links_config,
        "record": BibliographicRecordLinksSchemaV1
    }

    draft_links_config = {
        **RecordResourceConfig.draft_links_config,
        "record": BibliographicDraftLinksSchemaV1
    }

    error_map = {
        **RecordResourceConfig.error_map,
        ValidationError: handle_validation_error,
    }

    response_handlers = {
        **RecordResourceConfig.response_handlers,
        "application/vnd.inveniordm.v1+json": RecordResponse(
            UIJSONSerializer())
    }


class BibliographicRecordResource(RecordResource):
    """Bibliographic record resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_RECORD_CONFIG"
    default_config = BibliographicRecordResourceConfig


class BibliographicDraftResourceConfig(DraftResourceConfig):
    """Bibliographic draft resource configuration."""

    links_config = {
        **DraftResourceConfig.links_config,
        "record": BibliographicDraftLinksSchemaV1
    }


class BibliographicDraftResource(DraftResource):
    """Bibliographic record draft resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_DRAFT_CONFIG"
    default_config = BibliographicDraftResourceConfig


class BibliographicDraftActionResourceConfig(DraftActionResourceConfig):
    """Mock service configuration."""

    list_route = "/records/<pid_value>/draft/actions/<action>"

    action_commands = {
        "publish": "publish"
    }

    record_links_config = {
        **DraftActionResourceConfig.record_links_config,
        "record": BibliographicRecordLinksSchemaV1
    }


class BibliographicDraftActionResource(DraftActionResource):
    """Bibliographic record draft actions resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_DRAFT_ACTION_CONFIG"
    default_config = BibliographicDraftActionResourceConfig


class BibliographicUserRecordsResourceConfig(RecordResourceConfig):
    """Mock service configuration."""

    list_route = "/user/records"
    links_config = {
        "search": BibliographicUserRecordsSearchLinksSchemaV1
    }

    response_handlers = {
        **RecordResourceConfig.response_handlers,
        "application/vnd.inveniordm.v1+json": RecordResponse(
            UIJSONSerializer())
    }


class BibliographicUserRecordsResource(BibliographicRecordResource):
    """Bibliographic record user records resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_USER_RECORDS_CONFIG"
    default_config = BibliographicUserRecordsResourceConfig
