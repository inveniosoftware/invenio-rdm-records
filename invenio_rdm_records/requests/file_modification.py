# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""File modification request."""

from invenio_access.permissions import system_identity
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.uow import ModelCommitOp
from invenio_requests.customizations import RequestType, actions
from invenio_requests.proxies import current_requests_service
from invenio_search.api import dsl
from marshmallow import ValidationError, fields, validate

from invenio_rdm_records.proxies import current_rdm_records_service as records_service

from ..requests.base import BaseRequest


class CreateAction(actions.CreateAction):
    """Create action."""

    def execute(self, identity, uow):
        """Verify request preconditions and create the request."""
        record = self.request.topic.resolve()
        existing_requests = self._get_existing_requests(record)
        if existing_requests.total > 0:
            raise ValidationError(
                _("A file modification request for this record already exists."),
            )

        self.request["title"] = _(
            'File modification request for "{record_title}"'
        ).format(record_title=record.metadata["title"])

        super().execute(identity, uow)

    def _get_existing_requests(self, record):
        """Return existing open file modification requests for the record."""
        return current_requests_service.search(
            system_identity,
            extra_filter=dsl.Q(
                "bool",
                must=[
                    dsl.Q("term", **{"topic.record": record.pid.pid_value}),
                    dsl.Q("term", **{"type": FileModification.type_id}),
                    dsl.Q("term", **{"is_open": True}),
                ],
            ),
        )


class AcceptAction(actions.AcceptAction):
    """Accept action."""

    def execute(self, identity, uow, **kwargs):
        """Unlock the file bucket."""
        record = self.request.topic.resolve()
        draft = records_service.draft_cls.pid.resolve(record["id"])

        draft.files.unlock()
        uow.register(ModelCommitOp(draft.files.bucket))

        super().execute(identity, uow)


class FileModification(BaseRequest):
    """Request type for file modification."""

    type_id = "file-modification"
    name = _("File modification")

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
        "decline": actions.DeclineAction,
        "cancel": actions.CancelAction,
        "expire": actions.ExpireAction,
    }
    payload_schema = {
        "policy_id": fields.String(required=False),
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
    """Return the file modification request type from config.

    This function is only used to register the request type via the
    ``invenio_requests.types`` entrypoint, and allow to customize the request type
    class via the ``RDM_FILE_MODIFICATION_REQUEST_CLS`` application config.
    """
    if not app:
        return
    return app.config.get("RDM_FILE_MODIFICATION_REQUEST_CLS", FileModification)
