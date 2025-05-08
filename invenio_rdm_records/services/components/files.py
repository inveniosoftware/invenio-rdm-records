# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Service component taking care of files-related tasks such as setting the quota."""

from invenio_drafts_resources.services.records.components import DraftFilesComponent

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
