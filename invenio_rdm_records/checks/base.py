# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Checks integration with record check target."""

from invenio_checks.base import CheckTarget

from invenio_rdm_records.proxies import current_rdm_records_service as service


class RecordCheckTarget(CheckTarget):
    """CheckTarget class for records."""

    id = "record"

    def resolve(self, check_run):
        """Get the target object for a record check target."""
        if check_run.is_draft:
            return service.draft_cls.get_record(check_run.record_id)

        return service.record_cls.get_record(check_run.record_id)
