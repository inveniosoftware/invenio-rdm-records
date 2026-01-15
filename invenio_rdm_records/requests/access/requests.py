# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
# Copyright (C) 2024 KTH Royal Institute of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Access requests for records."""

from datetime import datetime, timedelta

import marshmallow as ma
from flask import g
from invenio_access.permissions import authenticated_user, system_identity
from invenio_drafts_resources.services.records.uow import ParentRecordCommitOp
from invenio_i18n import gettext as t
from invenio_i18n import lazy_gettext as _
from invenio_notifications.services.uow import NotificationOp
from invenio_requests import current_events_service
from invenio_requests.customizations import RequestType, actions
from invenio_requests.customizations.event_types import CommentEventType
from marshmallow import ValidationError, fields, validates
from marshmallow_utils.permissions import FieldPermissionsMixin

from invenio_rdm_records.notifications.builders import (
    GuestAccessRequestAcceptNotificationBuilder,
    GuestAccessRequestCancelNotificationBuilder,
    GuestAccessRequestDeclineNotificationBuilder,
    GuestAccessRequestSubmitNotificationBuilder,
    GuestAccessRequestSubmittedNotificationBuilder,
    UserAccessRequestAcceptNotificationBuilder,
    UserAccessRequestCancelNotificationBuilder,
    UserAccessRequestDeclineNotificationBuilder,
    UserAccessRequestSubmitNotificationBuilder,
)

from ...proxies import current_rdm_records_service as service


#
# Actions
#
class UserSubmitAction(actions.SubmitAction):
    """Submit action for user access requests."""

    def execute(self, identity, uow):
        """Execute the submit action."""
        self.request["title"] = self.request.topic.resolve().metadata["title"]
        uow.register(
            NotificationOp(
                UserAccessRequestSubmitNotificationBuilder.build(request=self.request)
            )
        )
        super().execute(identity, uow)


class UserCancelAction(actions.CancelAction):
    """Cancel action for user access requests."""

    def execute(self, identity, uow):
        """Execute the cancel action."""
        self.request["title"] = self.request.topic.resolve().metadata["title"]
        uow.register(
            NotificationOp(
                UserAccessRequestCancelNotificationBuilder.build(
                    request=self.request, identity=identity
                )
            )
        )
        super().execute(identity, uow)


class UserDeclineAction(actions.DeclineAction):
    """Decline action for user access requests."""

    def execute(self, identity, uow):
        """Execute the decline action."""
        self.request["title"] = self.request.topic.resolve().metadata["title"]
        uow.register(
            NotificationOp(
                UserAccessRequestDeclineNotificationBuilder.build(request=self.request)
            )
        )
        super().execute(identity, uow)


class GuestCancelAction(actions.CancelAction):
    """Cancel action for guest access requests."""

    def execute(self, identity, uow):
        """Execute the cancel action."""
        record = self.request.topic.resolve()
        self.request["title"] = record.metadata["title"]
        uow.register(
            NotificationOp(
                GuestAccessRequestCancelNotificationBuilder.build(
                    request=self.request, identity=identity
                )
            )
        )
        super().execute(identity, uow)


class GuestDeclineAction(actions.DeclineAction):
    """Decline action for guest access requests."""

    def execute(self, identity, uow):
        """Execute the decline action."""
        uow.register(
            NotificationOp(
                GuestAccessRequestDeclineNotificationBuilder.build(request=self.request)
            )
        )
        super().execute(identity, uow)


class GuestSubmitAction(actions.SubmitAction):
    """Submit action for guest access requests."""

    def execute(self, identity, uow):
        """Execute the submit action."""
        record = self.request.topic.resolve()
        self.request["title"] = record.metadata["title"]
        uow.register(
            NotificationOp(
                GuestAccessRequestSubmitNotificationBuilder.build(request=self.request)
            )
        )
        uow.register(
            NotificationOp(
                GuestAccessRequestSubmittedNotificationBuilder.build(
                    request=self.request
                )
            )
        )
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
            "description": t(
                "Requested by guest: %(full_name)s (%(email)s)",
                full_name=payload["full_name"],
                email=payload["email"],
            ),
            "origin": f"request:{self.request.id}",
        }

        # secret link will never expire if secret_link_expiration is empty
        days = int(payload["secret_link_expiration"])
        # TODO date calculation could be done elsewhere ?
        if days:
            data["expires_at"] = (
                (datetime.utcnow() + timedelta(days=days)).date().isoformat()
            )
        link = service.access.create_secret_link(identity, record.id, data)
        access_url = f"{record.links['self_html']}?token={link._link.token}"

        uow.register(
            ParentRecordCommitOp(
                record._record.parent, indexer_context=dict(service=service)
            )
        )
        uow.register(
            NotificationOp(
                GuestAccessRequestAcceptNotificationBuilder.build(
                    self.request, access_url=access_url
                )
            )
        )

        super().execute(identity, uow)

        confirmation_message = {
            "payload": {
                "content": _(
                    'Click <a href="%(url)s">here</a> to access the record.',
                    url=access_url,
                )
                % {"url": access_url}
            }
        }
        current_events_service.create(
            system_identity,
            self.request.id,
            confirmation_message,
            CommentEventType,
            uow=uow,
            notify=False,
        )


class UserAcceptAction(actions.AcceptAction):
    """Accept action."""

    def execute(self, identity, uow):
        """Accept user access request."""
        creator = self.request.created_by.resolve()
        record = self.request.topic.resolve()
        permission = self.request["payload"]["permission"]

        data = {
            "grants": [
                {
                    "permission": permission,
                    "subject": {
                        "type": "user",
                        "id": str(creator.id),
                    },
                    "origin": f"request:{self.request.id}",
                }
            ]
        }

        # NOTE: we're using the system identity here to avoid the grant creation
        #       potentially being blocked by the requesting user's profile visibility
        service.access.bulk_create_grants(system_identity, record.pid.pid_value, data)
        uow.register(
            ParentRecordCommitOp(record.parent, indexer_context=dict(service=service))
        )
        uow.register(
            NotificationOp(
                UserAccessRequestAcceptNotificationBuilder.build(self.request)
            )
        )

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

    endpoints_item = {
        "self_html": "invenio_app_rdm_requests.read_request"
    }

    available_actions = {
        "create": actions.CreateAction,
        "submit": UserSubmitAction,
        "delete": actions.DeleteAction,
        "accept": UserAcceptAction,
        "cancel": UserCancelAction,
        "decline": UserDeclineAction,
        "expire": actions.ExpireAction,
    }

    payload_schema = {
        "permission": fields.String(required=True),
        "message": fields.String(required=False),
    }


class EndpointsItemForGuestAccessRequest(dict):
    """This is to keep the pre-existing dynamic url logic while adopting new appproach.

    Pre-existing logic had "ui" part of link appended with
    - "/me" if authenticated user
    - "/access" if not

    The original logic is strange given that UserAccessRequest always appended "ui" part
    of link with "/access" (and there the user is authenticated). Nevertheless, this
    *tries* to keep the original logic, so that refactoring does not cause undue
    breaking changes.

    It tries to keep same logic, but has to make some concession: the previous code
    checked if the passed identity was authenticated and that identity was typically
    the g.identity. Because there is no access to the context from here now,
    we check the g.identity always. (this also could be resolved by addressing that
    wrinkle above and always selecting one endpoint)
    """

    def _self_html(self):
        """Return dynamic self_html endpoint."""
        endpoint = "invenio_app_rdm_requests.user_dashboard_request_view"

        if hasattr(g, "identity"):
            if authenticated_user not in g.identity.provides:
                endpoint = "invenio_app_rdm_requests.read_request"

        return endpoint

    def __getitem__(self, key):
        """Override `[]` access."""
        if key == "self_html":
            return self._self_html()
        else:
            return super().__getitem__(key)

    def get(self, key, default=None):
        """Override `.get` access."""
        if key == "self_html":
            return self._self_html()
        else:
            return super().get(key, default=default)


class GuestAccessRequest(RequestType):
    """Access request type coming from a guest."""

    type_id = "guest-access-request"
    name = _("Access request")

    creator_can_be_none = False
    topic_can_be_none = False
    allowed_creator_ref_types = ["email"]
    allowed_receiver_ref_types = ["user", "community"]
    allowed_topic_ref_types = ["record"]

    # passed dict is just to make instance non-empty
    endpoints_item = EndpointsItemForGuestAccessRequest({"self_html": True})

    @classmethod
    def _create_payload_cls(cls):
        class PayloadBaseSchema(ma.Schema, FieldPermissionsMixin):
            field_load_permissions = {
                "secret_link_expiration": "manage_access_options",
            }

            class Meta:
                unknown = ma.RAISE

        cls.payload_schema_cls = PayloadBaseSchema

    @validates("secret_link_expiration")
    def _validate_days(self, value):
        try:
            if int(value) < 0:
                raise ValidationError(
                    message=_("Not a valid number of days."),
                    field_name="secret_link_expiration",
                )
        except ValueError:
            raise ValidationError(
                message=_("Not a valid number of days."),
                field_name="secret_link_expiration",
            )

    available_actions = {
        "create": actions.CreateAction,
        "submit": GuestSubmitAction,
        "delete": actions.DeleteAction,
        "accept": GuestAcceptAction,
        "cancel": GuestCancelAction,
        "decline": GuestDeclineAction,
        "expire": actions.ExpireAction,
    }

    payload_schema = {
        "permission": fields.String(required=True),
        "email": fields.Email(required=True),
        "full_name": fields.String(required=True),
        "token": fields.String(required=True),
        "message": fields.String(required=True),
        "secret_link_expiration": fields.String(required=True),
        "consent_to_share_personal_data": fields.String(required=True),
    }
