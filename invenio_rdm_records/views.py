# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2022 Universität Hamburg.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Views."""

from flask import Blueprint

blueprint = Blueprint("invenio_rdm_records_ext", __name__)


def create_records_bp(app):
    """Create records blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.records_resource.as_blueprint()


def create_record_files_bp(app):
    """Create records files blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.record_files_resource.as_blueprint()


def create_draft_files_bp(app):
    """Create draft files blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.draft_files_resource.as_blueprint()


def create_record_media_files_bp(app):
    """Create records files blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.record_media_files_resource.as_blueprint()


def create_draft_media_files_bp(app):
    """Create draft files blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.draft_media_files_resource.as_blueprint()


def create_parent_record_links_bp(app):
    """Create parent record links blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.parent_record_links_resource.as_blueprint()


def create_parent_grants_bp(app):
    """Create record grants blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.parent_grants_resource.as_blueprint()


def create_grant_user_access_bp(app):
    """Create grant user access blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.grant_user_access_resource.as_blueprint()


def create_grant_group_access_bp(app):
    """Create grant group access blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.grant_group_access_resource.as_blueprint()


def create_pid_resolver_resource_bp(app):
    """Create pid resource blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.pid_resolver_resource.as_blueprint()


def create_community_records_bp(app):
    """Create community's records blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.community_records_resource.as_blueprint()


def create_record_communities_bp(app):
    """Create record communities blueprint."""
    return app.extensions[
        "invenio-rdm-records"
    ].record_communities_resource.as_blueprint()


def create_record_requests_bp(app):
    """Create record communities blueprint."""
    return app.extensions["invenio-rdm-records"].record_requests_resource.as_blueprint()


def create_oaipmh_server_blueprint_from_app(app):
    """Create app blueprint."""
    return app.extensions["invenio-rdm-records"].oaipmh_server_resource.as_blueprint()


def create_iiif_bp(app):
    """Create IIIF blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.iiif_resource.as_blueprint()


def create_collections_bp(app):
    """Create collections blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.collections_resource.as_blueprint()
