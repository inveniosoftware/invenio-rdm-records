# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2022 CERN.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2022 Universität Hamburg.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Views."""

from flask import (
    Blueprint,
    abort,
    current_app,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from invenio_access.permissions import system_identity
from invenio_i18n import lazy_gettext as _
from invenio_mail.tasks import send_email
from invenio_requests.proxies import current_requests_service
from invenio_requests.views.decorators import pass_request

from .proxies import current_rdm_records_service as current_service
from .requests.access.requests import GuestAcceptAction
from .services.errors import DuplicateAccessRequestError

blueprint = Blueprint("invenio_rdm_records_ext", __name__)


@blueprint.record_once
def init(state):
    """Init app."""
    app = state.app
    # Register services - cannot be done in extension because
    # Invenio-Records-Resources might not have been initialized.
    sregistry = app.extensions["invenio-records-resources"].registry
    ext = app.extensions["invenio-rdm-records"]
    sregistry.register(ext.records_service, service_id="records")
    sregistry.register(ext.records_service.files, service_id="files")
    sregistry.register(ext.records_service.draft_files, service_id="draft-files")
    sregistry.register(ext.records_media_files_service, service_id="record-media-files")
    sregistry.register(ext.records_media_files_service.files, service_id="media-files")
    sregistry.register(
        ext.records_media_files_service.draft_files, service_id="draft-media-files"
    )
    sregistry.register(ext.oaipmh_server_service, service_id="oaipmh-server")
    sregistry.register(ext.iiif_service, service_id="rdm-iiif")
    # Register indexers
    iregistry = app.extensions["invenio-indexer"].registry
    iregistry.register(ext.records_service.indexer, indexer_id="records")
    iregistry.register(ext.records_service.draft_indexer, indexer_id="records-drafts")


@blueprint.route("/access-requests/verify")
def verify_access_request_token():
    """UI endpoint for verifying guest access request tokens.

    When the token is verified successfully, a new guest access request will be created
    and the token object will be deleted from the database.
    The token value will be stored with the newly created request and grant access
    permissions to the request details.
    """
    token = request.args.get("access_request_token")
    access_request = None
    try:
        access_request = current_service.access.create_guest_access_request(
            identity=g.identity, token=token
        )
    except DuplicateAccessRequestError as e:
        if e.request_ids:
            duplicate_request = current_requests_service.read(
                identity=system_identity, id_=e.request_ids[0]
            )
            url = duplicate_request.links["self_html"]
            token = duplicate_request.data["payload"]["token"]
            return redirect(f"{url}?access_request_token={token}")

    if access_request is None:
        abort(404)

    url = f"{access_request.links['self_html']}?access_request_token={token}"

    send_email(
        {
            "subject": _("Access request submitted successfully"),
            "html_body": _(
                (
                    "Your access request was submitted successfully. "
                    'The request details are available <a href="%(url)s">here</a>.'
                ),
                url=url,
            ),
            "body": _(
                (
                    "Your access request was submitted successfully. "
                    "The request details are available at: %(url)s"
                ),
                url=url,
            ),
            "recipients": [access_request._request["created_by"]["email"]],
            "sender": current_app.config["MAIL_DEFAULT_SENDER"],
        }
    )

    return redirect(url)


@blueprint.route("/access-requests/requests/<request_pid_value>")
@pass_request(expand=True)
def read_request(request, **kwargs):
    """UI endpoint for the guest access request details."""
    request_type = request["type"]
    request_is_accepted = request["status"] == GuestAcceptAction.status_to

    # NOTE: this template is defined in Invenio-App-RDM
    return render_template(
        f"invenio_requests/{request_type}/index.html",
        user_avatar="",
        record=None,
        permissions={},
        invenio_request=request.to_dict(),
        request_is_accepted=request_is_accepted,
    )


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
