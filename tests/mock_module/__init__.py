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


def record_file_download(pid_value, file_item=None, is_preview=False, **kwargs):
    """Fake record_file_download view function."""
    return "<file content>"


def create_invenio_app_rdm_records_blueprint(app):
    """Create fake invenio_app_rdm_records Blueprint akin to invenio-app-rdm's."""
    blueprint = Blueprint(
        "invenio_app_rdm_records",
        __name__,
    )

    # Records URL rules
    blueprint.add_url_rule(
        "/records/<pid_value>/files/<path:filename>",
        view_func=record_file_download,
    )

    return blueprint


def verify_access_request_token():
    """Fake verifiy_access_request_token view function.

    Notice lack of parameters to test querystring injection.
    """
    return "<verification>"


def create_invenio_app_rdm_requests_blueprint(app):
    """Create fake invenio_app_rdm_requests Blueprint akin to invenio-app-rdm's."""
    blueprint = Blueprint(
        "invenio_app_rdm_requests",
        __name__,
    )

    # Requests URL rules
    blueprint.add_url_rule(
        "/access/requests/confirm", view_func=verify_access_request_token
    )

    return blueprint


def create_invenio_app_rdm_communities_blueprint(app):
    """Create fake invenio_app_rdm_communities Blueprint akin to invenio-app-rdm's."""
    blueprint = Blueprint(
        "invenio_app_rdm_communities",
        __name__,
    )

    def communities_home(pid_value, community, community_ui):
        return "<communities home>"

    # Requests URL rules
    blueprint.add_url_rule("/communities/<pid_value>/", view_func=communities_home)

    return blueprint
