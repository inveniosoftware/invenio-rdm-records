# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-Rdm-Records is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Sort parameter interpreter API."""

from invenio_access.permissions import authenticated_user
from invenio_records_resources.services.records.params.base import ParamInterpreter

from invenio_rdm_records.records.systemfields.deletion_status import (
    RecordDeletionStatusEnum,
)


class StatusParam(ParamInterpreter):
    """Evaluates the 'status' parameter."""

    def apply(self, identity, search, params):
        """Evaluate the status parameter on the search."""
        value = params.pop("status", None)
        if value is not None and value in [x.value for x in RecordDeletionStatusEnum]:
            search = search.filter("term", **{"deletion_status": value})
        return search


class PublishedRecordsParam(ParamInterpreter):
    """Evaluates the include_deleted parameter."""

    def apply(self, identity, search, params):
        """Evaluate the include_deleted parameter on the search."""
        value = params.pop("include_deleted", None)
        # Filter prevents from displaying deleted records on mainsite search
        # deleted records should appear only in admins panel
        if value is None:
            search = search.filter(
                "term", **{"deletion_status": RecordDeletionStatusEnum.PUBLISHED.value}
            )
        return search


class MyDraftsParam(ParamInterpreter):
    """Evaluates the include_deleted parameter."""

    def apply(self, identity, search, params):
        """Evaluate the include_deleted parameter on the search."""
        value = params.pop("include_deleted", None)

        # Filter prevents from other users' drafts from displaying on Moderator's
        # dashboard
        def is_user_authenticated():
            return authenticated_user in identity.provides

        if value is None and is_user_authenticated():
            search = search.filter(
                "term", **{"parent.access.owned_by.user": identity.id}
            )
        return search


class MetricsParam(ParamInterpreter):
    """Evaluates the metrics parameter."""

    def apply(self, identity, search, params):
        """Evaluate the metrics parameter on the search.

        Usage:

        .. code-block:: python

            "params": {
                ...
                "metrics": {
                    "total_data": {
                        "name": "total_data",
                        "type": "sum",
                        "kwargs": {
                            "field": "files.totalbytes"
                        }
                    }
                }
            }
        """
        value = params.pop("metrics", {})
        for key, metric_params in value.items():
            name = metric_params.get("name", key)
            _type = metric_params.get("type", None)
            kwargs = metric_params.get("kwargs", {})
            if name and _type:
                search.aggs.metric(name, _type, **kwargs)
        return search
