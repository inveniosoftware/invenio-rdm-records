# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""File Service API."""

from invenio_records_resources.services import FileService

from invenio_rdm_records.services.errors import RecordDeletedException


class RDMFileService(FileService):
    """A service for adding files support to records."""

    def _check_record_deleted_permissions(self, record, identity):
        """Ensure that the record exists (not deleted) or raise."""
        if record.is_draft:
            return
        if record.deletion_status.is_deleted:
            can_read_deleted = self.check_permission(
                identity, "read_deleted_files", record=record
            )
            if not can_read_deleted:
                raise RecordDeletedException(record)

    def _get_record(self, id_, identity, action, file_key=None):
        """Get the associated record."""
        record = super()._get_record(id_, identity, action, file_key)
        self._check_record_deleted_permissions(record, identity)

        return record
