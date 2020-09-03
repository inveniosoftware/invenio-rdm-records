# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Service."""

from invenio_drafts_resources.services import RecordDraftService, \
    RecordDraftServiceConfig
from invenio_records_resources.services import MarshmallowDataValidator

from .links import DraftSelfHtmlLinkBuilder, RecordSelfHtmlLinkBuilder
from .marshmallow import MetadataSchemaV1
from .models import BibliographicRecord, BibliographicRecordDraft
from .permissions import RDMRecordPermissionPolicy
from .pid_manager import BibliographicPIDManager
from .resources import BibliographicDraftActionResourceConfig, \
    BibliographicDraftResourceConfig, BibliographicRecordResourceConfig
from .search import BibliographicRecordsSearch


class BibliographicRecordServiceConfig(RecordDraftServiceConfig):
    """Bibliografic record draft service config."""

    # Record
    record_cls = BibliographicRecord
    permission_policy_cls = RDMRecordPermissionPolicy
    data_validator = MarshmallowDataValidator(
        schema=MetadataSchemaV1
    )
    pid_manager = BibliographicPIDManager()
    record_route = BibliographicRecordResourceConfig.item_route
    record_search_route = BibliographicRecordResourceConfig.list_route
    record_files_route = record_route + "/files"
    search_cls = BibliographicRecordsSearch
    record_link_builders = RecordDraftServiceConfig.record_link_builders + [
        RecordSelfHtmlLinkBuilder,
    ]

    # Draft
    draft_cls = BibliographicRecordDraft
    draft_data_validator = data_validator
    draft_route = BibliographicDraftResourceConfig.list_route
    draft_action_route = BibliographicDraftActionResourceConfig.list_route
    draft_link_builders = RecordDraftServiceConfig.draft_link_builders + [
        DraftSelfHtmlLinkBuilder,
    ]


class BibliographicRecordService(RecordDraftService):
    """Bibliographic record service."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_SERVICE_CONFIG"
    default_config = BibliographicRecordServiceConfig
