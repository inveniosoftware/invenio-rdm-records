# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Views."""


def create_blueprints_from_app(app):
    """Create blueprints."""

def create_records_bp(app):
    """Create records blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.records_resource.as_blueprint(
            "bibliographic_records_resource"
        )


def create_records_versions_bp(app):
    """Create records versions blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.records_versions_resource.as_blueprint(
            "bibliographic_records_versions_resource"
        )


def create_drafts_bp(app):
    """Create drafts blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.drafts_resource.as_blueprint(
            "bibliographic_draft_resource"
        )


def create_drafts_action_bp(app):
    """Create drafts action blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.drafts_action_resource.as_blueprint(
            "bibliographic_draft_action_resource"
        )


def create_user_records_bp(app):
    """Create user records blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.user_records_resource.as_blueprint(
            "bibliographic_user_records_resource"
        )


def create_record_files_bp(app):
    """Create records files blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.record_files_resource.as_blueprint(
            "bibliographic_record_files_resource"
        )


def create_record_files_action_bp(app):
    """Create records files action blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.record_files_action_resource.as_blueprint(
            "bibliographic_record_files_action_resource"
        )


def create_draft_files_bp(app):
    """Create draft files blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.draft_files_resource.as_blueprint(
            "bibliographic_draft_files_resource"
        )


def create_draft_files_action_bp(app):
    """Create draft files action blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.draft_files_action_resource.as_blueprint(
            "bibliographic_draft_files_action_resource"
        )


def create_parent_record_links_bp(app):
    """Create parent record links blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.parent_record_links_resource.as_blueprint(
            "bibliographic_parent_links_resource"
        )
