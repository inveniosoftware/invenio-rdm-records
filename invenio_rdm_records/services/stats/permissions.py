# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio RDM Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permissions for the statistics endpoint from Invenio-Stats."""

from flask import g
from invenio_stats import current_stats

from ...proxies import current_rdm_records_service as records_service


class StatsPermissionTranslator:
    """Translator class between the statistics endpoint and the service layer."""

    def __init__(self, action_name, service=None, **params):
        """Constructor."""
        self.service = service or records_service
        self.action_name = action_name
        self.params = params

    def translate_params(self, identity):
        """Translate the params between the stats endpoint and the records service.

        This method acts as a translation layer between the statistics API endpoint
        and the records service and is intended to be overridden by potential
        subclasses. It takes the ``params`` from the query and translates
        them into something that can be used by the records service (as keyword
        arguments) to check for permissions.
        For example, the query ``params`` might provide a ``recid`` value, but the
        permission generators may require a ``record`` class. This could be retrieved
        in this method.
        """
        return self.params

    def can(self):
        """Check if the action is allowed for the current identity."""
        return self.service.check_permission(
            g.identity, self.action_name, **self.translate_params(g.identity)
        )


def permissions_policy_lookup_factory(query_name, params):
    """Factory that looks up the permissions from the permission policy per default.

    If the query in question has a specific permission factory defined, this one will
    be used. Otherwise, it will look up the 'query_stats' permission from the active
    RDM records service.
    """
    if current_stats.queries[query_name].permission_factory is None:
        return StatsPermissionTranslator("query_stats", **params)
    else:
        return current_stats.queries[query_name].permission_factory(query_name, params)
