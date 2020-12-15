# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Views."""


def create_records_bp(app):
    """Create records blueprint."""
    ext = app.extensions
    return ext["invenio-rdm-records"].records_resource.as_blueprint(
            "bibliographic_records_resource"
        )


def create_drafts_bp(app):
    """Create drafts blueprint."""
    ext = app.extensions
    return ext["invenio-rdm-records"].drafts_resource.as_blueprint(
            "bibliographic_draft_resource"
        )


def create_drafts_action_bp(app):
    """Create drafts action blueprint."""
    ext = app.extensions
    return ext["invenio-rdm-records"].drafts_action_resource.as_blueprint(
            "bibliographic_draft_action_resource"
        )


def create_user_records_bp(app):
    """Create user records blueprint."""
    ext = app.extensions
    return ext["invenio-rdm-records"].user_records_resource.as_blueprint(
            "bibliographic_user_records_resource"
        )


def create_record_files_bp(app):
    """Create records files blueprint."""
    ext = app.extensions
    return ext["invenio-rdm-records"].record_files_resource.as_blueprint(
            "bibliographic_record_files_resource"
        )


def create_record_files_action_bp(app):
    """Create records files action blueprint."""
    ext = app.extensions
    return ext[
        "invenio-rdm-records"].record_files_action_resource.as_blueprint(
            "bibliographic_record_files_action_resource"
        )


def create_draft_files_bp(app):
    """Create draft files blueprint."""
    ext = app.extensions
    return ext["invenio-rdm-records"].draft_files_resource.as_blueprint(
            "bibliographic_draft_files_resource"
        )


def create_draft_files_action_bp(app):
    """Create draft files action blueprint."""
    ext = app.extensions
    return ext["invenio-rdm-records"].draft_files_action_resource.as_blueprint(
            "bibliographic_draft_files_action_resource"
        )
