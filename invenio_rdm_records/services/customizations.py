# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2022 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Helpers for customizing the configuration in a controlled manner."""


class FromConfigPIDsProviders:
    """Data descriptor for pid providers configuration."""

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

        pids = obj._app.config.get("RDM_PERSISTENT_IDENTIFIERS", {})
        providers = {
            p.name: p
            for p in obj._app.config.get("RDM_PERSISTENT_IDENTIFIER_PROVIDERS", [])
        }
        doi_enabled = obj._app.config.get("DATACITE_ENABLED", False)

        return {
            scheme: get_provider_dict(conf, providers)
            for scheme, conf in pids.items()
            if scheme != "doi" or doi_enabled
        }


class FromConfigRequiredPIDs:
    """Data descriptor for required pids configuration."""

    def __get__(self, obj, objtype=None):
        """Return required pids (descriptor protocol)."""
        pids = obj._app.config.get("RDM_PERSISTENT_IDENTIFIERS", {})
        doi_enabled = obj._app.config.get("DATACITE_ENABLED", False)

        pids = {
            scheme: conf
            for (scheme, conf) in pids.items()
            if scheme != "doi" or doi_enabled
        }
        return [
            scheme for (scheme, conf) in pids.items() if conf.get("required", False)
        ]
