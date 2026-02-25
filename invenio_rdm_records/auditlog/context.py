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


class DiffContext(object):
    """Payload generator for setting comparable audit log metadata."""

    def __call__(self, data, **kwargs):
        """Update data with before and after keys."""
        before = kwargs.get("before")
        after = kwargs.get("after")
        if before is None and after is None:
            return

        dict_set(data, "metadata.before", before)
        dict_set(data, "metadata.after", after)


class ResourceContext(object):
    """Payload generator for setting resource data."""

    def __call__(self, data, **kwargs):
        """Update data with resource data."""
        resource = kwargs["triggered_by"]
        triggered_by = {
            "id": resource.pid.pid_value,
            "type": "draft" if isinstance(resource, RDMDraft) else "record",
        }
        dict_set(data, "metadata.triggered_by", triggered_by)
