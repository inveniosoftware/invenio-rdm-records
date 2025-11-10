# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record deletion request."""

from invenio_access.permissions import system_identity
from invenio_i18n import lazy_gettext as _
from invenio_notifications.services.uow import NotificationOp
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_requests.customizations import RequestType, actions
from invenio_requests.proxies import current_requests_service
from invenio_search.api import dsl
from invenio_vocabularies.proxies import current_service as current_vocabularies_service
from marshmallow import ValidationError, fields, validate
from sqlalchemy.exc import NoResultFound

from invenio_rdm_records.notifications.builders import (
    RecordDeletionAcceptNotificationBuilder,
    RecordDeletionDeclineNotificationBuilder,
)
from invenio_rdm_records.proxies import current_rdm_records_service


class CreateAction(actions.CreateAction):
    """Create action."""

    def execute(self, identity, uow):
        """Verify request preconditions and create the request."""
        record = self.request.topic.resolve()
        existing_requests = self._get_existing_requests(record)
        if existing_requests.total > 0:
            raise ValidationError(
                _("A deletion request for this record already exists."),
            )

        self._verify_removal_reason()
        self.request["title"] = _('Deletion request for "{record_title}"').format(
            record_title=record.metadata["title"]
        )

        super().execute(identity, uow)

    def _get_existing_requests(self, record):
        """Return existing open deletion requests for the record."""
        return current_requests_service.search(
            system_identity,
            extra_filter=dsl.Q(
                "bool",
                must=[
                    dsl.Q("term", **{"topic.record": record.pid.pid_value}),
                    dsl.Q("term", **{"type": RecordDeletion.type_id}),
                    dsl.Q("term", **{"is_open": True}),
                ],
            ),
        )

    def _verify_removal_reason(self):
        invalid_reason_msg = _("Invalid removal reason")
        removal_reason_id = self.request.get("payload", {}).get("reason")
        try:
            vocab = current_vocabularies_service.read(
                identity=system_identity, id_=("removalreasons", removal_reason_id)
            )
            if "deletion-request" not in vocab.data.get("tags", []):
                raise ValidationError(invalid_reason_msg)
        except (PIDDoesNotExistError, NoResultFound):
            raise ValidationError(invalid_reason_msg)


class AcceptAction(actions.AcceptAction):
    """Accept action."""

    def execute(self, identity, uow, **kwargs):
        """Delete the record."""
        record = self.request.topic.resolve()
        request_creator = self.request.created_by.resolve()

        removal_reason_id = self.request.get("payload", {}).get("reason")
        tombstone_data = {
            "removal_reason": {"id": removal_reason_id},
        }

        # For immediate deletions, we track the deletion policy ID in the tombstone
        policy_id = self.request.get("payload", {}).get("policy_id")
        if policy_id:
            # NOTE: Deletion policies are not a vocabulary, but we follow the same
            # format for consistency and potential extensions.
            tombstone_data["deletion_policy"] = {"id": policy_id}
            tombstone_data["removed_by"] = {"user": str(request_creator.id)}
        else:
            remover = (
                identity.id if identity is system_identity else str(identity.user.id)
            )
            tombstone_data["removed_by"] = {"user": remover}

        current_rdm_records_service.delete_record(
            identity, record["id"], tombstone_data, uow=uow
        )

        if kwargs.get("send_notification", True):
            uow.register(
                NotificationOp(
                    RecordDeletionAcceptNotificationBuilder.build(request=self.request)
                )
            )

        super().execute(identity, uow)


class DeclineAction(actions.DeclineAction):
    """Decline action."""

    def execute(self, identity, uow, **kwargs):
        """Decline the request."""
        if kwargs.get("send_notification", True):
            uow.register(
                NotificationOp(
                    RecordDeletionDeclineNotificationBuilder.build(request=self.request)
                )
            )
        super().execute(identity, uow)


class RecordDeletion(RequestType):
    """Request type for record deletion."""

    type_id = "record-deletion"
    name = _("Record deletion")

    creator_can_be_none = False
    topic_can_be_none = True
    receiver_can_be_none = True
    allowed_creator_ref_types = ["user"]
    allowed_receiver_ref_types = ["user"]
    allowed_topic_ref_types = ["record"]
    needs_context = {
        "record_permission": "preview",
    }
    resolve_topic_needs = True

    available_actions = {
        "create": CreateAction,
        "submit": actions.SubmitAction,
        "delete": actions.DeleteAction,
        "accept": AcceptAction,
        "decline": DeclineAction,
        "cancel": actions.CancelAction,
        "expire": actions.ExpireAction,
    }
    payload_schema = {
        "policy_id": fields.String(required=False),
        "reason": fields.String(required=True, validate=validate.Length(min=1)),
        "comment": fields.String(
            required=False,
            validate=validate.Length(min=25),
            allow_none=True,
        ),
    }

    def _update_link_config(self, **context_vars):
        """Fix the prefix required for `self_html`."""
        prefix = "/me"
        return {"ui": context_vars["ui"] + prefix}


def get_request_type(app):
    """Return the record deletion request type from config.

    This function is only used to register the request type via the
    ``invenio_requests.types`` entrypoint, and allow to customize the request type
    class via the ``RDM_RECORD_DELETION_REQUEST_CLS`` application config.
    """
    if not app:
        return
    return app.config.get("RDM_RECORD_DELETION_REQUEST_CLS", RecordDeletion)
