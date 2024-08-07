# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2023 CERN.
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Helpers for customizing the configuration in a controlled manner."""


class FromConfigPIDsProviders:
    """Data descriptor for pid providers configuration."""

    def __init__(self, pids_key=None, providers_key=None):
        """Initialize the config descriptor."""
        self.pids_key = pids_key or "RDM_PERSISTENT_IDENTIFIERS"
        self.providers_key = providers_key or "RDM_PERSISTENT_IDENTIFIER_PROVIDERS"

    def __get__(self, obj, objtype=None):
        """Return value that was grafted on obj (descriptor protocol)."""

        def get_provider_dict(pid_config, pid_providers):
            """Return pid provider dict in shape expected by config users.

            (This transformation would be unnecesary if the pid_providers were
            in the right shape already).
            """
            provider_dict = {"default": None}

            for name in pid_config.get("providers", []):
                # This may throw a KeyError which is a sign that the config
                # is wrong.
                provider_dict[name] = pid_providers[name]
                provider_dict["default"] = provider_dict["default"] or name

            return provider_dict

        pids = obj._app.config.get(self.pids_key, {})
        providers = {p.name: p for p in obj._app.config.get(self.providers_key, [])}
        return {
            scheme: get_provider_dict(conf, providers)
            for scheme, conf in pids.items()
            if conf["is_enabled"](obj._app)
        }


class FromConfigRequiredPIDs:
    """Data descriptor for required pids configuration."""

    def __init__(self, pids_key=None):
        """Initialize the config descriptor."""
        self.pids_key = pids_key or "RDM_PERSISTENT_IDENTIFIERS"

    def __get__(self, obj, objtype=None):
        """Return required pids (descriptor protocol)."""
        pids = obj._app.config.get(self.pids_key, {})
        return [
            scheme
            for (scheme, conf) in pids.items()
            if (conf["is_enabled"](obj._app) and conf.get("required", False))
        ]


class FromConfigConditionalPIDs:
    """Data descriptor for conditional pids."""

    def __init__(self, pids_key=None):
        """Initialize the config descriptor."""
        self.pids_key = pids_key or "RDM_PERSISTENT_IDENTIFIERS"

    def __get__(self, obj, objtype=None):
        """Return conditional pids (descriptor protocol)."""
        pids = obj._app.config.get(self.pids_key, {})
        result = {}
        for scheme, conf in pids.items():
            condition_func = conf.get("condition")
            if callable(condition_func):
                result[scheme] = condition_func
        return result
