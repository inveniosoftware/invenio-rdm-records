# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Result items for secret link operations of the services."""

from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_records_resources.services.base.results import \
    ServiceItemResult, ServiceListResult
from marshmallow_utils.links import LinksFactory


def _current_host():
    """Function used to provide the current hostname to the link store."""
    if current_app:
        return current_app.config['SITE_HOSTNAME']
    return None


class SecretLinkItem(ServiceItemResult):
    """Single link result."""

    def __init__(
        self, service, identity, link, errors=None, links_config=None
    ):
        """Constructor."""
        self._errors = errors
        self._identity = identity
        self._links_config = links_config
        self._link = link
        self._service = service
        self._data = None

    @property
    def id(self):
        """Get the link id."""
        return str(self._link.id)

    @property
    def data(self):
        """Property to get the link's dumped data."""
        if self._data:
            return self._data

        links = LinksFactory(host="", config=self._links_config)
        self._data = self._service.schema_secret_link.dump(
            self._link.to_dict(),
            context=dict(
                identity=self._identity,
                # TODO is this required in any way?
                links_namespace="secret_link",
                links_factory=links,
            )
        )

        return self._data

    def to_dict(self):
        """Get a dictionary for the record."""
        res = self.data
        if self._errors:
            res["errors"] = self._errors

        return res


class SecretLinkList(ServiceListResult):
    """List of records result."""

    def __init__(self, service, identity, results, links_config=None):
        """Constructor."""
        self._service = service
        self._identity = identity
        self._results = results
        self._links_config = links_config

    def __len__(self):
        """Return the total numer of hits."""
        return len(self._results)

    def __iter__(self):
        """Iterator over the hits."""
        return iter(self.results)

    @property
    def results(self):
        """Iterator over the hits."""
        links = LinksFactory(host=_current_host, config=self._links_config)

        for res in self._results:
            # Project the record
            projection = self._service.schema_secret_link.dump(
                res.to_dict(),
                context=dict(
                    identity=self._identity,
                    links_namespace="secret_link",
                    links_factory=links,
                )
            )
            yield projection

    def to_dict(self):
        """Return result as a dictionary."""
        # TODO with the "hits", we're kind of mimicking an ES result...
        #      should we simplify this?
        res = {
            "hits": {
                "hits": list(self.results),
                "total": len(self),
            },
        }
        return res
