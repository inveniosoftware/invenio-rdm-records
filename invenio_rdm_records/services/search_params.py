# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-Rdm-Records is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Search parameter interpreter API."""

from invenio_access.permissions import authenticated_user
from invenio_records_resources.services.records.params.base import ParamInterpreter
from invenio_search.engine import dsl

from invenio_rdm_records.records.systemfields.deletion_status import (
    RecordDeletionStatusEnum,
)
from invenio_rdm_records.services.generators import AccessGrant


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


class SharedOrMyDraftsParam(ParamInterpreter):
    """Evaluates the shared_with_me parameter.

    Returns only drafts owned by the user or shared with the user via grant subject user or role.
    """

    def _generate_shared_with_me_query(self, identity):
        """Generate the shared_with_me query."""
        tokens = []
        for _permission in ["preview", "edit", "manage"]:
            tokens.extend(AccessGrant(_permission)._grant_tokens(identity))
        return dsl.Q("terms", **{"parent.access.grant_tokens": tokens})

    def apply(self, identity, search, params):
        """Evaluate the include_deleted parameter on the search."""
        value = params.pop("include_deleted", None)

        # Filter prevents from other users' drafts from displaying on Moderator's
        # dashboard
        def is_user_authenticated():
            return authenticated_user in identity.provides

        if value is None and is_user_authenticated():
            if params.get("shared_with_me") is True:
                # Shared with me
                shared_with_me = self._generate_shared_with_me_query(identity)
                search = search.filter(shared_with_me)
            elif params.get("shared_with_me") is False:
                # My uploads
                my_uploads = dsl.Q(
                    "term", **{"parent.access.owned_by.user": identity.id}
                )
                search = search.filter(my_uploads)
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
