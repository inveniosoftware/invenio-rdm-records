# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-Rdm-Records is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Sort parameter interpreter API."""

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
