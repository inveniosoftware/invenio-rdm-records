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

from .marshmallow import MetadataSchemaV1
from .models import BibliographicRecord, BibliographicRecordDraft
from .permissions import RDMRecordPermissionPolicy
from .pid_manager import BibliographicPIDManager
from .resources import BibliographicDraftActionResourceConfig, \
    BibliographicDraftResourceConfig, BibliographicRecordResourceConfig


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

    # Draft
    draft_cls = BibliographicRecordDraft
    draft_data_validator = MarshmallowDataValidator(
        schema=MetadataSchemaV1
    )
    draft_route = BibliographicDraftResourceConfig.list_route
    draft_action_route = BibliographicDraftActionResourceConfig.list_route


class BibliographicRecordService(RecordDraftService):
    """Bibliographic record service."""

    default_config = BibliographicRecordServiceConfig
