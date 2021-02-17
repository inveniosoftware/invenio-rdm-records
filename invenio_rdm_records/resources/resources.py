# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Resource."""

from flask import g
from flask_resources.context import resource_requestctx
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

    def search(self):
        """Perform a search over the items."""
        identity = g.identity
        hits = self.service.search_drafts(
            identity=identity,
            params=resource_requestctx.url_args,
            links_config=self.config.links_config,
            es_preference=self._get_es_preference()
        )
        return hits.to_dict(), 200


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
