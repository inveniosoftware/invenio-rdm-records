# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utils for Invenio RDM Records."""

from flask import current_app, request
from copy import deepcopy


def is_doi_locally_managed(doi_value):
    """Determine if a DOI value is locally managed."""
    return any(doi_value.startswith(prefix) for prefix in
               current_app.config['RDM_RECORDS_LOCAL_DOI_PREFIXES'])


class DynamicAggregation(dict):
    """Aggregation that is fully resolved in the request context."""

    def __init__(self, base_agg, function_agg):
        """."""
        self.function_agg = function_agg
        super(DynamicAggregation, self).__init__(base_agg)

    def __call__(self):
        """."""
        res = deepcopy(self)
        return self.function_agg(res)


def community_collections_agg(agg):
    """Aggregation function for the community collections."""
    community_id = request.args.get('community')
    if community_id:
        agg['terms']['include'] = community_id+':.*'
    return agg
