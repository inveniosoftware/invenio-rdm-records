# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2025 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Community addition request."""

from invenio_access.permissions import system_identity
from invenio_i18n import lazy_gettext as _
from invenio_requests.customizations import CommentEventType, RequestType, actions
from invenio_requests.proxies import current_events_service, current_requests_service
from invenio_search.api import dsl
from invenio_vocabularies.proxies import current_service as current_vocabularies_service
from marshmallow import ValidationError, fields

from invenio_rdm_records.proxies import current_rdm_records_service


class CreateAction(actions.CreateAction):
    """Create action."""

    def check_existing_request(self, record):
        """Check if record was rejected from EU community."""
        record_requests = dsl.Q(
            "bool",
            must=[
                dsl.Q("term", **{"topic.record": record.pid.pid_value}),
            ],
        )
        request_types = dsl.Q(
            "bool",
            should=[
                dsl.Q("term", **{"type": RecordDeletion.type_id}),
            ],
            must_not=[
                dsl.Q(
                    "exists",
                    **{"field": "receiver"},
                ),
            ],
            minimum_should_match=1,
        )
        finalq = record_requests & request_types
        results = current_requests_service.search(system_identity, extra_filter=finalq)

        # NOTE Didn't add an open search filter on open requests since this could useful in implementing
        # Other rules like max number deletion requests allowed.
        for result in results:
            if result["is_open"]:
                return True
        return False

    def execute(self, identity, uow):
        """Execute the create action."""
        record = self.request.topic.resolve()
        if self.check_existing_request(record):
            raise ValidationError(
                _("A request for this record already exists."),
            )

        super().execute(identity, uow)


class SubmitAction(actions.SubmitAction):
    """Submit action."""

    def execute(self, identity, uow, **kwargs):
        """Execute the submit action."""
        record = self.request.topic.resolve()
        self.request["title"] = record.metadata["title"]

        removal_reason_id = self.request.get("payload", {}).get("reason")
        if not removal_reason_id:
            raise ValidationError(_("Removal reason is required."))
        vocab = current_vocabularies_service.read(
            identity=system_identity, id_=("removalreasons", removal_reason_id)
        )

        # TODO Move to config?
        comment_content = f"""
        <b>Record deletion request created.</b>
        <br/><br/>
        <strong>Reason:</strong> {vocab.data["title"]["en"]}
        <br/>
        <strong>Comment:</strong> {self.request.get('payload', {}).get('comment', '')}
        <br/><br/>
        Record created: {record.created.isoformat()}
        """
        comment = {"payload": {"content": comment_content}}
        current_events_service.create(
            system_identity,
            self.request.id,
            comment,
            CommentEventType,
            notify=False,
            uow=uow,
        )

        super().execute(identity, uow, **kwargs)


class AcceptAction(actions.AcceptAction):
    """Accept action."""

    def execute(self, identity, uow, **kwargs):
        """Delete the record."""
        record = self.request.topic.resolve()
        tombstone_data = {"note": "Record deleted by uploader"}

        # TODO This might return PIDDoesNotExist error
        removal_reason_id = self.request.get("payload", {}).get("reason")
        if not removal_reason_id:
            raise ValidationError(_("Removal reason is required."))
        vocab = current_vocabularies_service.read(
            identity=system_identity, id_=("removalreasons", removal_reason_id)
        )
        tombstone_data["removal_reason"] = {"id": vocab.id}

        current_rdm_records_service.delete_record(
            system_identity, record["id"], tombstone_data, uow=uow
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
        "submit": SubmitAction,
        "delete": actions.DeleteAction,
        "accept": AcceptAction,
        "decline": actions.DeclineAction,
        "cancel": actions.CancelAction,
        "expire": actions.ExpireAction,
    }
    payload_schema = {
        "reason": fields.String(required=True),
        "comment": fields.String(required=False, allow_none=True),
    }


def get_request_type(app):
    """Return the record deletion request type from config.

    This function is only used to register the request type via the
    ``invenio_requests.types`` entrypoint, and allow to customize the request type
    class via the ``RDM_RECORD_DELETION_REQUEST_CLS`` application config.
    """
    if not app:
        return
    return app.config.get("RDM_RECORD_DELETION_REQUEST_CLS", RecordDeletion)
