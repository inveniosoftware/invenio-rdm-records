# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Mock test module.

It has to exist here to be picked up correctly by the create_app of
tests/resources/conftest.py .
"""

from flask import Blueprint


def create_invenio_app_rdm_records_blueprint(app):
    """Create fake invenio_app_rdm_records Blueprint akin to invenio-app-rdm's."""
    blueprint = Blueprint(
        "invenio_app_rdm_records",
        __name__,
    )

    @blueprint.route("/records/<pid_value>/files/<path:filename>")
    def record_file_download(pid_value, file_item=None, is_preview=False, **kwargs):
        """Fake record_file_download view function."""
        return "<file content>"

    @blueprint.route("/records/<pid_value>")
    def record_detail(pid_value, file_item=None, is_preview=False, **kwargs):
        """Fake record_detail view function."""
        return "<record detail>"

    @blueprint.route("/uploads/<pid_value>")
    def deposit_edit(pid_value, file_item=None, is_preview=False, **kwargs):
        """Fake record_detail view function."""
        return "<deposit edit>"

    @blueprint.route("/records/<pid_value>/latest")
    def record_latest(record=None, **kwargs):
        """Fake record_latest view function."""
        return "<record latest>"

    @blueprint.route("/<any(doi):pid_scheme>/<path:pid_value>")
    def record_from_pid(record=None, **kwargs):
        """Fake record_from_pid view function."""
        return "<record from pid>"

    return blueprint


def create_invenio_app_rdm_requests_blueprint(app):
    """Create fake invenio_app_rdm_requests Blueprint akin to invenio-app-rdm's."""
    blueprint = Blueprint(
        "invenio_app_rdm_requests",
        __name__,
    )

    @blueprint.route("/access/requests/confirm")
    def verify_access_request_token(request, **kwargs):
        """Fake verifiy_access_request_token view function.

        Notice lack of parameters to test querystring injection.
        """
        return "<verification>"

    @blueprint.route("/me/requests/<request_pid_value>")
    def user_dashboard_request_view(request, **kwargs):
        """Fake user_dashboard_request_view function."""
        return "<user dashboard request view>"

    @blueprint.route("/access/requests/<request_pid_value>")
    def read_request(request, **kwargs):
        """Fake read_request function (could have used the real one but no need atm)."""
        return "<read request>"

    return blueprint


def create_invenio_app_rdm_communities_blueprint(app):
    """Create fake invenio_app_rdm_communities Blueprint akin to invenio-app-rdm's."""
    blueprint = Blueprint(
        "invenio_app_rdm_communities",
        __name__,
    )

    @blueprint.route("/communities/<pid_value>/")
    def communities_home(pid_value, community, community_ui):
        return "<communities home>"

    return blueprint
