# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Access requests for records."""
from datetime import datetime

import arrow
from flask import current_app, g
from invenio_access.permissions import authenticated_user, system_identity
from invenio_i18n import lazy_gettext as _
from invenio_mail.tasks import send_email
from invenio_records_resources.services.uow import Operation, RecordCommitOp
from invenio_requests.customizations import RequestType, actions
from marshmallow import ValidationError, fields

from ...proxies import current_rdm_records_service as service
from ...records import RDMRecord


class EmailOp(Operation):
    """A notification operation."""

    def __init__(self, receiver, subject, html_body, body):
        """Initialize operation."""
        self.receiver = receiver
        self.subject = subject
        self.html_body = html_body
        self.body = body

    def on_post_commit(self, uow):
        """Start task to send text via email."""
        send_email(
            {
                "subject": self.subject,
                "html_body": self.html_body,
                "body": self.body,
                "recipients": [self.receiver],
                "sender": current_app.config["MAIL_DEFAULT_SENDER"],
            }
        )


#
# Actions
#
class UserSubmitAction(actions.SubmitAction):
    """Submit action for user access requests."""

    def execute(self, identity, uow):
        """Execute the submit action."""
        self.request["title"] = self.request.topic.resolve().metadata["title"]
        super().execute(identity, uow)


class GuestSubmitAction(actions.SubmitAction):
    """Submit action for guest access requests."""

    def execute(self, identity, uow):
        """Execute the submit action."""
        self.request["title"] = self.request.topic.resolve().metadata["title"]

        record = RDMRecord.pid.resolve(self.request["topic"]["record"])
        exp = record.parent.access.settings.secret_link_expiration
        expires_at = (
            arrow.now().shift(days=exp).date().isoformat() if exp is not None else ""
        )
        self.request["payload"]["secret_link_expiration"] = expires_at

        super().execute(identity, uow)


class GuestAcceptAction(actions.AcceptAction):
    """Accept action."""

    def execute(self, identity, uow):
        """Accept guest access request."""
        record = service.read(
            id_=self.request.topic.reference_dict["record"], identity=system_identity
        )
        payload = self.request["payload"]

        # NOTE: the description isn't translated because it can be changed later
        #       by the record owner
        data = {
            "permission": payload["permission"],
            "description": (
                f"Requested by guest: {payload['full_name']} ({payload['email']})"
            ),
            "origin": f"request:{self.request.id}",
        }

        # secret link will never expire if secret_link_expiration is empty
        secret_link_expiration = payload["secret_link_expiration"]
        if secret_link_expiration != "":
            data["expires_at"] = secret_link_expiration

        link = service.access.create_secret_link(identity, record.id, data)
        access_url = f"{record.links['self_html']}?token={link._link.token}"
        plain_message = _("Access the record here: %(url)s", url=access_url)
        message = _(
            'Click <a href="%(url)s">here</a> to access the record.', url=access_url
        )

        uow.register(RecordCommitOp(record._record.parent))
        uow.register(
            EmailOp(
                receiver=payload["email"],
                subject="Request accepted",
                body=plain_message,
                html_body=message,
            )
        )

        super().execute(identity, uow)


class UserAcceptAction(actions.AcceptAction):
    """Accept action."""

    def execute(self, identity, uow):
        """Accept user access request."""
        creator = self.request.created_by.resolve()
        record = self.request.topic.resolve()
        permission = self.request["payload"]["permission"]

        data = {
            "permission": permission,
            "subject": {
                "type": "user",
                "id": str(creator.id),
            },
            "origin": f"request:{self.request.id}",
        }

        # NOTE: we're using the system identity here to avoid the grant creation
        #       potentially being blocked by the requesting user's profile visibility
        service.access.create_grant(system_identity, record.pid.pid_value, data)
        uow.register(RecordCommitOp(record.parent))

        super().execute(identity, uow)


#
# Requests
#
class UserAccessRequest(RequestType):
    """Access request type coming from a user."""

    type_id = "user-access-request"
    name = _("Access request")

    creator_can_be_none = False
    topic_can_be_none = False
    allowed_creator_ref_types = ["user"]
    allowed_receiver_ref_types = ["user", "community"]
    allowed_topic_ref_types = ["record"]

    def _update_link_config(self, **context_vars):
        """Update the 'ui' variable for generation of links."""
        return {"ui": context_vars["ui"] + "/me"}

    available_actions = {
        "create": actions.CreateAction,
        "submit": UserSubmitAction,
        "delete": actions.DeleteAction,
        "accept": UserAcceptAction,
        "cancel": actions.CancelAction,
        "decline": actions.DeclineAction,
        "expire": actions.ExpireAction,
    }

    payload_schema = {
        "permission": fields.String(required=True),
        "message": fields.String(required=False),
    }


class GuestAccessRequest(RequestType):
    """Access request type coming from a guest."""

    type_id = "guest-access-request"
    name = _("Access request")

    creator_can_be_none = False
    topic_can_be_none = False
    allowed_creator_ref_types = ["email"]
    allowed_receiver_ref_types = ["user", "community"]
    allowed_topic_ref_types = ["record"]

    def _update_link_config(self, **context_vars):
        """Fix the prefix required for "self_html"."""
        identity = context_vars.get("identity", g.identity)
        prefix = "/me"
        if authenticated_user not in identity.provides:
            prefix = "/access-requests"

        return {"ui": context_vars["ui"] + prefix}

    def _validate_date(value):
        if value == "":
            return True

        try:
            expires_at = datetime.fromisoformat(value)

            if expires_at < datetime.now():
                raise ValidationError(
                    message="Expiration date must be set to the future",
                    field_name="secret_link_expiration",
                )
        except ValueError:
            raise ValidationError(
                message="Not a valid date.",
                field_name="secret_link_expiration",
            )

    available_actions = {
        "create": actions.CreateAction,
        "submit": GuestSubmitAction,
        "delete": actions.DeleteAction,
        "accept": GuestAcceptAction,
        "cancel": actions.CancelAction,
        "decline": actions.DeclineAction,
        "expire": actions.ExpireAction,
    }

    payload_schema = {
        "permission": fields.String(required=True),
        "email": fields.Email(required=True),
        "full_name": fields.String(required=True),
        "token": fields.String(required=True),
        "message": fields.String(required=False),
        "secret_link_expiration": fields.String(required=True, validate=_validate_date),
    }
