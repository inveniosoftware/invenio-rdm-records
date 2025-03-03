# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-Rdm-Records is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Search parameter interpreter API."""

from invenio_search.engine import dsl

from invenio_access.permissions import authenticated_user
from invenio_records_resources.services.records.params.base import ParamInterpreter

from invenio_rdm_records.records.systemfields.access.grants import Grant
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


class SharedOrMyDraftsParam(ParamInterpreter):
    """Evaluates the shared_with_me parameter.

    Returns only drafts owned by the user or shared with the user via grant subject user or role.
    """

    def _make_grant_token(self, subj_type, subj_id, permission):
        """Create a grant token from the specified parts."""
        # NOTE: `Grant.to_token()` doesn't need the actual subject to be set
        return Grant(
            subject=None,
            origin=None,
            permission=permission,
            subject_type=subj_type,
            subject_id=subj_id,
        ).to_token()

    def _grant_tokens(self, identity, permissions):
        """Parse a list of grant tokens provided by the given identity."""
        tokens = []
        for _permission in permissions:
            for need in identity.provides:
                token = None
                if need.method == "id":
                    token = self._make_grant_token("user", need.value, _permission)
                elif need.method == "role":
                    token = self._make_grant_token("role", need.value, _permission)

                if token is not None:
                    tokens.append(token)

        return tokens

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
                tokens = self._grant_tokens(
                    identity, permissions=["preview", "edit", "manage"]
                )
                shared_with_me = dsl.Q(
                    "terms", **{"parent.access.grant_tokens": tokens}
                )
                return search.filter(shared_with_me)
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
