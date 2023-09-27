# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Sort parameter interpreter API."""

from flask import current_app
from invenio_records_resources.services.records.params.sort import SortParam


class VerifiedRecordsSortParam(SortParam):
    """Evaluate the 'sort' parameter for RDM records."""

    def apply(self, identity, search, params):
        """Evaluate the sort parameter on the search.

        If the config "RDM_SEARCH_SORT_BY_VERIFIED" is set, then all the sorting is
        prepended by the record's `is_verified` property.
        """
        if current_app.config["RDM_SEARCH_SORT_BY_VERIFIED"]:
            fields = self._compute_sort_fields(params)
            return search.sort(*["-parent.is_verified", *fields])
        return super().apply(identity, search, params)
