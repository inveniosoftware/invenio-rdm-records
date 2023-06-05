# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Result items for secret link operations of the services."""

from flask import current_app
from invenio_records_resources.services.base.results import (
    ServiceItemResult,
    ServiceListResult,
)
from invenio_records_resources.services.records.results import FieldsResolver
from marshmallow_utils.links import LinksFactory


def _current_host():
    """Function used to provide the current hostname to the link store."""
    if current_app:
        return current_app.config["SITE_API_URL"]
    return None


class SecretLinkItem(ServiceItemResult):
    """Single link result."""

    def __init__(self, service, identity, link, errors=None, links_config=None):
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
            ),
        )

        return self._data

    def to_dict(self):
        """Get a dictionary for the grant."""
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
                ),
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


class GrantItem(ServiceItemResult):
    """Single grant result."""

    def __init__(
        self,
        service,
        identity,
        grant,
        errors=None,
        expandable_fields=None,
        expand=False,
    ):
        """Constructor."""
        self._errors = errors
        self._identity = identity
        self._grant = grant
        self._service = service
        self._expand = expand
        self._fields_resolver = FieldsResolver(expandable_fields or [])
        self._data = None

    @property
    def data(self):
        """Property to get the grant's dumped data."""
        if self._data:
            return self._data

        self._data = self._service.schema_grant.dump(
            self._grant.to_dict(),
            context={"identity": self._identity},
        )

        if self._expand:
            self._fields_resolver.resolve(self._identity, [self._data])
            fields = self._fields_resolver.expand(self._identity, self._data)
            self._data["expanded"] = fields

        return self._data

    def to_dict(self):
        """Get a dictionary for the record."""
        res = self.data
        if self._errors:
            res["errors"] = self._errors

        return res


class GrantList(ServiceListResult):
    """List of grant results."""

    def __init__(
        self,
        service,
        identity,
        results,
        expandable_fields=None,
        expand=False,
    ):
        """Constructor."""
        self._service = service
        self._identity = identity
        self._results = results
        self._fields_resolver = FieldsResolver(expandable_fields or [])
        self._expand = expand

    def __len__(self):
        """Return the total numer of hits."""
        return len(self._results)

    def __iter__(self):
        """Iterator over the hits."""
        return iter(self.results)

    @property
    def results(self):
        """Iterator over the hits."""
        for i, res in enumerate(self._results):
            # Project the record
            projection = self._service.schema_grant.dump(
                res.to_dict(),
                context={"identity": self._identity},
            )

            # NOTE: the "id" is just the index
            projection["id"] = i
            yield projection

    def to_dict(self):
        """Return result as a dictionary."""
        hits = list(self.results)

        if self._expand:
            self._fields_resolver.resolve(self._identity, hits)
            for hit in hits:
                fields = self._fields_resolver.expand(self._identity, hit)
                hit["expanded"] = fields

        res = {
            "hits": {
                "hits": hits,
                "total": len(self),
            },
        }
        return res
