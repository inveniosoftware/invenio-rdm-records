# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""File Service API."""

from invenio_audit_logs.services.uow import AuditLogOp
from invenio_records_resources.services import FileService
from invenio_records_resources.services.uow import unit_of_work

from invenio_rdm_records.auditlog.actions import (
    FileCreateAuditLog,
    FileDeleteAuditLog,
)
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

    @unit_of_work()
    def commit_file(self, identity, id_, file_key, uow=None):
        """Commit a file upload."""
        result = super().commit_file(identity, id_, file_key, uow=uow)

        uow.register(
            AuditLogOp(FileCreateAuditLog.build(identity, id_, file_key=file_key))
        )  # Added here as audit logs can't be added to invenio-records-resources
        return result

    @unit_of_work()
    def delete_file(self, identity, id_, file_key, uow=None):
        """Delete a file."""
        result = super().delete_file(identity, id_, file_key, uow=uow)

        uow.register(
            AuditLogOp(FileDeleteAuditLog.build(identity, id_, file_key=file_key))
        )  # Added here as audit logs can't be added to invenio-records-resources
        return result
