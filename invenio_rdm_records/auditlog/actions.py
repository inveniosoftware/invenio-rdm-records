# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Action registration via entrypoint function."""

import marshmallow as ma
from invenio_audit_logs.services.schema import ResourceSchema
from invenio_drafts_resources.auditlog.actions import BaseAuditLog
from invenio_i18n import lazy_gettext as _

from invenio_rdm_records.services.schemas.parent.access import (
    AccessSettingsSchema,
    Grant,
)

from .context import LogChangesContext, ResourceDataContext


class ParentBaseAuditLog(BaseAuditLog):
    """Base class for audit log builders for parent records."""

    resource_type = "parent"

    context = BaseAuditLog.context + [
        LogChangesContext(),
        ResourceDataContext(),
    ]

    metadata_schema = {
        **BaseAuditLog.metadata_schema,
        "triggered_by": ma.fields.Nested(
            ResourceSchema,
            required=True,
        ),
    }


class RDMRecordGrantAuditLog(ParentBaseAuditLog):
    """Audit log for record grant update."""

    id = "record.grant_update"
    message_template = _(
        "User {user_id} updated access of {resource_type} {resource_id} via record."
    )

    metadata_schema = {
        **ParentBaseAuditLog.metadata_schema,
        "before": ma.fields.List(
            ma.fields.Nested(Grant),
            required=True,
        ),
        "after": ma.fields.List(
            ma.fields.Nested(Grant),
            required=True,
        ),
    }


class RDMDraftGrantAuditLog(RDMRecordGrantAuditLog):
    """Audit log for draft grant update."""

    id = "draft.grant_update"
    message_template = _(
        "User {user_id} updated access of {resource_type} {resource_id} via draft."
    )


class SecretLinkAuditLogSchema(ma.Schema):
    """Schema for a secret link."""

    class Meta:
        """Meta attributes for schema."""

        unknown = ma.EXCLUDE

    id = ma.fields.String()
    permission = ma.fields.String()


class RDMRecordSecretLinkAuditLog(ParentBaseAuditLog):
    """Audit log for record secret link update."""

    id = "record.secret_link_update"
    message_template = _(
        "User {user_id} updated secret link of {resource_type} {resource_id} via record."
    )

    metadata_schema = {
        **ParentBaseAuditLog.metadata_schema,
        "before": ma.fields.Nested(SecretLinkAuditLogSchema, required=True),
        "after": ma.fields.Nested(SecretLinkAuditLogSchema, required=True),
    }


class RDMDraftSecretLinkAuditLog(RDMRecordSecretLinkAuditLog):
    """Audit log for draft secret link update."""

    id = "draft.secret_link_update"
    message_template = _(
        "User {user_id} updated secret link of {resource_type} {resource_id} via draft."
    )


class RDMRecordAccessSettingsAuditLog(ParentBaseAuditLog):
    """Audit log for record access settings update."""

    id = "record.access_settings_update"
    message_template = _(
        "User {user_id} updated access settings of {resource_type} {resource_id} via record."
    )

    metadata_schema = {
        **ParentBaseAuditLog.metadata_schema,
        "before": ma.fields.Nested(AccessSettingsSchema, required=True),
        "after": ma.fields.Nested(AccessSettingsSchema, required=True),
    }


class RDMDraftAccessSettingsAuditLog(RDMRecordAccessSettingsAuditLog):
    """Audit log for draft access settings update."""

    id = "draft.access_settings_update"
    message_template = _(
        "User {user_id} updated access settings of {resource_type} {resource_id} via draft."
    )
