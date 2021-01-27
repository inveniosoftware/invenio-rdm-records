# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Resource."""

from invenio_drafts_resources.resources import DraftActionResource, \
    DraftFileActionResource, DraftFileResource, DraftResource, \
    RecordResource
from invenio_records_resources.resources.files import FileActionResource, \
    FileResource

from . import config


#
# Records
#
class RDMRecordResource(RecordResource):
    """Bibliographic record resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_RECORD_CONFIG"
    default_config = config.RDMRecordResourceConfig


#
# Drafts
#
class RDMDraftResource(DraftResource):
    """Bibliographic record draft resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_DRAFT_CONFIG"
    default_config = config.RDMDraftResourceConfig


class RDMDraftActionResource(DraftActionResource):
    """Bibliographic record draft actions resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_DRAFT_ACTION_CONFIG"
    default_config = config.RDMDraftActionResourceConfig


#
# User records
#
class RDMUserRecordsResource(RDMRecordResource):
    """Bibliographic record user records resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_USER_RECORDS_CONFIG"
    default_config = config.RDMUserRecordsResourceConfig


#
# Record files
#
class RDMRecordFilesResource(FileResource):
    """Bibliographic record files resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_RECORD_FILES_CONFIG"
    default_config = config.RDMRecordFilesResourceConfig


class RDMRecordFilesActionResource(FileActionResource):
    """Bibliographic record files action resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_RECORD_FILES_ACTION_CONFIG"
    default_config = config.RDMRecordFilesActionResourceConfig


#
# Draft files
#
class RDMDraftFilesResource(DraftFileResource):
    """Bibliographic record files resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_DRAFT_FILES_CONFIG"
    default_config = config.RDMDraftFilesResourceConfig


class RDMDraftFilesActionResource(DraftFileActionResource):
    """Bibliographic record files action resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_DRAFT_FILES_ACTION_CONFIG"
    default_config = config.RDMDraftFilesActionResourceConfig
