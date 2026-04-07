# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Audit log context resolvers."""

from invenio_records.dictutils import dict_set

from invenio_rdm_records.records.api import RDMDraft


class LogChangesContext(object):
    """Payload generator for setting comparable audit log metadata."""

    def __call__(self, data, **kwargs):
        """Update data with before and after keys."""
        before = kwargs.get("before", {})
        after = kwargs.get("after", {})

        dict_set(data, "metadata.before", before)
        dict_set(data, "metadata.after", after)


class ResourceDataContext(object):
    """Payload generator for setting resource data."""

    def __call__(self, data, **kwargs):
        """Update data with resource data."""
        resource = kwargs.get("triggered_by", None)
        if resource is None:
            return
        triggered_by = {
            "id": resource.pid.pid_value,
            "type": "draft" if isinstance(resource, RDMDraft) else "record",
        }
        dict_set(data, "metadata.triggered_by", triggered_by)


class FileContext(object):
    """Payload generator for setting file data."""

    def __call__(self, data, **kwargs):
        """Update data with file data."""
        file_key = kwargs.get("file_key", None)
        dict_set(data, "metadata.file_key", file_key)
