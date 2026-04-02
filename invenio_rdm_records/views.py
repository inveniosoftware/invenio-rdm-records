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

from types import SimpleNamespace

from flask import Blueprint, abort, current_app, render_template
from flask_login import current_user, login_required
from invenio_records_resources.services.files.transfer import constants

from .proxies import current_rdm_records_storage_service

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


def create_community_collections_bp(app):
    """Create community collections blueprint."""
    ext = app.extensions["invenio-rdm-records"]
    return ext.community_collections_resource.as_blueprint()


@blueprint.app_context_processor
def file_transfer_type():
    """Injects all *_TRANSFER_TYPE constants into templates as `file_transfer_type`, accessible via dot notation."""
    file_transfer_type_constants = {
        name.replace("_TRANSFER_TYPE", ""): getattr(constants, name)
        for name in dir(constants)
        if name.endswith("_TRANSFER_TYPE") and not name.startswith("_")
    }

    return {"transfer_types": file_transfer_type_constants}


def _format_storage(data):
    """Format storage data for UI."""
    BYTES_TO_GB = 10**9
    rows = []

    for e in data["entries"]:
        item = e["item"]
        record = e["record"]

        rows.append(
            {
                "title": item.get("metadata", {}).get("title", "Empty title"),
                "url": item["links"]["self_html"],
                "additional_quota": round(e["extra_quota"] / BYTES_TO_GB, 1),
                "used": round(e["used_bytes"] / BYTES_TO_GB, 1),
                "total": round(
                    (data["default_quota"] + e["extra_quota"]) / BYTES_TO_GB, 1
                ),
                "date": item.get("metadata", {}).get("publication_date", ""),
                "status": "Draft" if not record.is_published else "Published",
            }
        )

    return {
        "default_quota": round(data["default_quota"] / BYTES_TO_GB, 1),
        "total_allowed_quota": round(data["max_additional_quota"] / BYTES_TO_GB, 1),
        "additional_granted_quota": round(data["total_extra"] / BYTES_TO_GB, 1),
        "additional_used_quota": round(data["total_used"] / BYTES_TO_GB, 1),
        "additional_available_quota": round(
            max(data["max_additional_quota"] - data["total_extra"], 0) / BYTES_TO_GB, 1
        ),
        "records": rows,
    }


@blueprint.route("/account/settings/quota/", endpoint="storage_settings")
@login_required
def storage_settings():
    """User storage page."""
    if not current_app.config.get(
        "RDM_IMMEDIATE_QUOTA_INCREASE_ENABLED", False
    ) or not getattr(current_user, "verified_at", None):
        abort(404)

    result = current_rdm_records_storage_service.get_user_storage_usage(current_user)

    storage = _format_storage(result)

    return render_template(
        "invenio_rdm_records/settings/storage.html",
        storage=storage,
    )
