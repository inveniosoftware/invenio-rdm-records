# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Resource."""

from flask import abort, g
from flask_resources.context import resource_requestctx
from invenio_drafts_resources.resources import DraftActionResource, \
    DraftFileActionResource, DraftFileResource, DraftResource, \
    RecordResource, RecordVersionsResource
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


class RDMRecordVersionsResource(RecordVersionsResource):
    """Bibliographic record versions resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_RECORD_VERSIONS_CONFIG"
    default_config = config.RDMRecordVersionsResourceConfig


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


#
# Parent Record Links
#
class RDMParentRecordLinksResource(RecordResource):
    """Secret links resource."""

    config_name = "RDM_RECORDS_BIBLIOGRAPHIC_PARENT_RECORD_LINKS_CONFIG"
    default_config = config.RDMParentRecordLinksResourceConfig

    def create(self):
        """Create a secret link for a record."""
        item = self.service.create_secret_link(
            id_=resource_requestctx.route["pid_value"],
            identity=g.identity,
            data=resource_requestctx.request_content,
            links_config=self.config.links_config
        )

        return item.to_dict(), 201

    def read(self):
        """Read a secret link for a record."""
        item = self.service.read_secret_link(
            id_=resource_requestctx.route["pid_value"],
            identity=g.identity,
            link_id=resource_requestctx.route["link_id"],
            links_config=self.config.links_config,
        )
        return item.to_dict(), 200

    def update(self):
        """Update a secret link for a record."""
        abort(405)

    def partial_update(self):
        """Patch a secret link for a record."""
        item = self.service.update_secret_link(
            id_=resource_requestctx.route["pid_value"],
            identity=g.identity,
            link_id=resource_requestctx.route["link_id"],
            data=resource_requestctx.request_content,
            links_config=self.config.links_config
        )

        return item.to_dict(), 200

    def delete(self):
        """Delete a a secret link for a record."""
        self.service.delete_secret_link(
            id_=resource_requestctx.route["pid_value"],
            identity=g.identity,
            link_id=resource_requestctx.route["link_id"],
            links_config=self.config.links_config
        )
        return None, 204

    def search(self):
        """List secret links for a record."""
        items = self.service.read_secret_links(
            id_=resource_requestctx.route["pid_value"],
            identity=g.identity,
            links_config=self.config.links_config
        )
        return items.to_dict(), 200
