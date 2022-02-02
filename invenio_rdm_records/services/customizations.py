# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2022 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Helpers for customizing the configuration in a controlled manner."""

from invenio_base.utils import load_or_import_from_config

from ..searchconfig import SearchConfig


#
# Helpers
#
def _make_cls(cls, attrs):
    """Make the custom config class."""
    return type(f'Custom{cls.__name__}', (cls, ), attrs, )


#
# Mixins
#
class SearchOptionsMixin:
    """Customization of search options."""

    @classmethod
    def customize(cls, opts):
        """Customize the search options."""
        attrs = {}
        if opts.facets:
            attrs['facets'] = opts.facets
        if opts.sort_options:
            attrs['sort_options'] = opts.sort_options
            attrs['sort_default'] = opts.sort_default
            attrs['sort_default_no_query'] = opts.sort_default_no_query
        return _make_cls(cls, attrs) if attrs else cls


class FromConfig:
    """Data descriptor to connect config with application configuration.

    See https://docs.python.org/3/howto/descriptor.html .

    .. code-block:: python

        # service/config.py
        class ServiceConfig:
            foo = FromConfig("FOO", default=1)

        # config.py
        FOO = 2

        # ext.py
        c = ServiceConfig.build(app)
        c.foo  # 2
    """

    def __init__(self, config_key, default=None, import_string=False):
        """Constructor for data descriptor."""
        self.config_key = config_key
        self.default = default
        self.import_string = import_string

    def __get__(self, obj, objtype=None):
        """Return value that was grafted on obj (descriptor protocol)."""
        if self.import_string:
            return load_or_import_from_config(
                app=obj._app, key=self.config_key, default=self.default
            )
        else:
            return obj._app.config.get(self.config_key, self.default)

    def __set_name__(self, owner, name):
        """Store name of grafted field (descriptor protocol)."""
        # If we want to allow setting it we can implement this.
        pass

    def __set__(self, obj, value):
        """Set value on grafted_field of obj (descriptor protocol)."""
        # If we want to allow setting it we can implement this.
        pass


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
                provider_dict['default'] = provider_dict['default'] or name

            return provider_dict

        pids = obj._app.config.get("RDM_PERSISTENT_IDENTIFIERS", {})
        providers = {
            p.name: p for p in
            obj._app.config.get("RDM_PERSISTENT_IDENTIFIER_PROVIDERS", [])
        }
        doi_enabled = obj._app.config.get("DATACITE_ENABLED", False)

        return {
            scheme: get_provider_dict(conf, providers)
            for scheme, conf in pids.items()
            if scheme != 'doi' or doi_enabled
        }


class FromConfigRequiredPIDs:
    """Data descriptor for required pids configuration."""

    def __get__(self, obj, objtype=None):
        """Return required pids (descriptor protocol)."""
        pids = obj._app.config.get("RDM_PERSISTENT_IDENTIFIERS", {})
        doi_enabled = obj._app.config.get("DATACITE_ENABLED", False)

        pids = {
            scheme: conf for (scheme, conf) in pids.items()
            if scheme != 'doi' or doi_enabled
        }
        return [
            scheme for (scheme, conf) in pids.items()
            if conf.get("required", False)
        ]


class FromConfigSearchOptions:
    """Data descriptor for search options configuration."""

    def __init__(self, config_key, default=None, search_option_cls=None):
        """Constructor for data descriptor."""
        self.config_key = config_key
        self.default = default or {}
        self.search_option_cls = search_option_cls

    def __get__(self, obj, objtype=None):
        """Return value that was grafted on obj (descriptor protocol)."""
        search_opts = obj._app.config.get(self.config_key, self.default)
        sort_opts = obj._app.config.get('RDM_SORT_OPTIONS')
        facet_opts = obj._app.config.get('RDM_FACETS')

        search_config = SearchConfig(
            search_opts,
            sort=sort_opts,
            facets=facet_opts,
        )

        return self.search_option_cls.customize(search_config)


class ConfiguratorMixin:
    """Shared customization for requests service config."""

    @classmethod
    def build(cls, app):
        """Build the config object."""
        return type(f"Custom{cls.__name__}", (cls,), {"_app": app})()
