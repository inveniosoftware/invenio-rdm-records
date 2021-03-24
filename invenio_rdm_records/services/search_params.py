# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Sort parameter interpreter API."""

from invenio_records_resources.services.records.params.base import \
    ParamInterpreter


class AllVersionsUserRecordsParam(ParamInterpreter):
    """Evaluates the 'allversions' parameter."""

    def apply(self, identity, search, params):
        """Evaluate the allversions parameter on the search."""
        if not params.get("allversions"):
            search = search.filter('term', versions__is_latest_draft=True)

        # else all versions are returned

        return search
