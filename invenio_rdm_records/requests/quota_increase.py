# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Quota increase request."""

from invenio_access.permissions import system_identity
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.uow import ModelCommitOp
from invenio_requests.customizations import RequestType, actions
from invenio_requests.proxies import current_requests_service
from invenio_search.api import dsl
from marshmallow import ValidationError, fields, validate

from invenio_rdm_records.proxies import current_rdm_records_service as records_service


class CreateAction(actions.CreateAction):
    """Create action."""

    def execute(self, identity, uow):
        """Verify request preconditions and create the request."""
        # record = self.request.topic.resolve()

        self.request["title"] = "Quota increase request"

        super().execute(identity, uow)


class AcceptAction(actions.AcceptAction):
    """Accept action."""

    def execute(self, identity, uow, **kwargs):
        """Apply the quota increase."""
        DRAFT = int(self.request.get("topic", {}).get("record"))
        QUOTA_SIZE = int(self.request.get("payload", {}).get("quota_size"))
        data = {
            "notes": str(self.request.id),
            "quota_size": QUOTA_SIZE * 1000000000,
            "max_file_size": QUOTA_SIZE * 1000000000,
        }
        records_service.set_quota(system_identity, DRAFT, data)

        super().execute(identity, uow)


class QuotaIncrease(RequestType):
    """Request type for quota increase."""

    type_id = "quota-increase"
    name = _("Quota increase")

    creator_can_be_none = False
    topic_can_be_none = False
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
    payload_schema = {"quota_size": fields.String(required=True)}

    def _update_link_config(self, **context_vars):
        """Fix the prefix required for `self_html`."""
        prefix = "/me"
        return {"ui": context_vars["ui"] + prefix}


def get_request_type(app):
    """Return the quota increase request type from config.

    This function is only used to register the request type via the
    ``invenio_requests.types`` entrypoint, and allow to customize the request type
    class via the ``RDM_QUOTA_INCREASE_REQUEST_CLS`` application config.
    """
    if not app:
        return
    return app.config.get("RDM_QUOTA_INCREASE_REQUEST_CLS", QuotaIncrease)
