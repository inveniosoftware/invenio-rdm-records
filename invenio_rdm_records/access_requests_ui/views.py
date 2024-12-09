# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Access request UI views."""

from flask import abort, current_app, g, redirect, render_template, request
from invenio_access.permissions import system_identity
from invenio_i18n import lazy_gettext as _
from invenio_mail.tasks import send_email
from invenio_requests.proxies import current_requests_service
from invenio_requests.views.decorators import pass_request

from ..proxies import current_rdm_records_service as current_service
from ..requests.access.requests import GuestAcceptAction
from ..services.errors import AccessRequestExistsError

# Attention! These views are registered on the API app


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
    except AccessRequestExistsError as e:
        access_request = current_requests_service.read(
            identity=system_identity, id_=e.request_id
        )
        if e.request_id:
            url = access_request.links["self_html"]
            token = access_request.data["payload"]["token"]
            return redirect(f"{url}?access_request_token={token}")

    if access_request is None:
        abort(404)

    url = f"{access_request.links['self_html']}?access_request_token={token}"

    return redirect(url)


@pass_request(expand=True)
def read_request(request, **kwargs):
    """UI endpoint for the guest access request details."""
    request_type = request["type"]
    request_is_accepted = request["status"] == GuestAcceptAction.status_to

    # NOTE: this template is defined in Invenio-App-RDM
    return render_template(
        f"invenio_requests/{request_type}/index.html",
        user_avatar=None,
        record=None,
        permissions={},
        invenio_request=request.to_dict(),
        request_is_accepted=request_is_accepted,
    )
