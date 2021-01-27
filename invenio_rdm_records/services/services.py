# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Service."""

from invenio_drafts_resources.services.records import RecordDraftService
from invenio_records_resources.services.files.service import RecordFileService
from invenio_records_resources.services.records.service import RecordService

from . import config


class RDMRecordService(RecordDraftService):
    """Bibliographic record service."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_SERVICE_CONFIG"
    default_config = config.RDMRecordServiceConfig


class RDMUserRecordsService(RecordService):
    """Bibliographic user records service."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_USER_RECORDS_SERVICE_CONFIG"
    default_config = config.RDMUserRecordsServiceConfig


#
# Record files
#
class RDMRecordFilesService(RecordFileService):
    """Bibliographic record files service."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_RECORD_FILES_SERVICE_CONFIG"
    default_config = config.RDMRecordFilesServiceConfig


#
# Draft files
#
class RDMDraftFilesService(RecordFileService):
    """Bibliographic draft files service."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_DRAFT_FILES_SERVICE_CONFIG"
    default_config = config.RDMDraftFilesServiceConfig
