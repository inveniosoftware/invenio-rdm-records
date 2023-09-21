# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-Rdm-Records is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Sort parameter interpreter API."""
from flask_login import current_user
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
        if value is None and current_user.is_authenticated:
            search = search.filter(
                "term", **{"parent.access.owned_by.user": current_user.id}
            )
        return search
