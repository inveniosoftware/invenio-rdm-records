# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
# Copyright (C) 2026 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Service component taking care of files-related tasks such as setting the quota."""

from datetime import datetime, timezone

from flask import current_app
from invenio_drafts_resources.services.records.components import DraftFilesComponent
from marshmallow import ValidationError

from ...records.api import get_files_quota


class RDMDraftFilesComponent(DraftFilesComponent):
    """Record/draft files component with yummy RDM flavor."""

    def create(self, identity, data=None, record=None, errors=None):
        """Assigns files.enabled and sets the bucket's quota size & max file size."""
        super().create(identity, data=data, record=record, errors=errors)

        quota = get_files_quota(record)
        if quota_size := quota.get("quota_size"):
            record.files.bucket.quota_size = quota_size

        if max_file_size := quota.get("max_file_size"):
            record.files.bucket.max_file_size = max_file_size

    def publish(self, identity, draft=None, record=None, errors=None):
        """Check if files modified can be published."""
        # Check if modified files are being published after modification period
        can_manage_files = self.service.check_permission(
            identity, "manage_files", record=draft
        )
        file_mod_enabled = current_app.config.get(
            "RDM_IMMEDIATE_FILE_MODIFICATION_ENABLED"
        )
        modification_period = current_app.config.get("RDM_FILE_MODIFICATION_PERIOD")
        if (
            file_mod_enabled
            and record.is_published  # Draft should be of a published record
            and not can_manage_files  # This allows admins to bypass the check
            and not draft.files.bucket.locked  # Only if the bucket is still unlocked
        ):
            if (datetime.now(timezone.utc) - record.created) > modification_period:
                raise ValidationError(
                    current_app.config.get(
                        "RDM_FILE_MODIFICATION_VALIDATION_ERROR_MESSAGE"
                    )
                )

        super().publish(identity, draft=draft, record=record)
