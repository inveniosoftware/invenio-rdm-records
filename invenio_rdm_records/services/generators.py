# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-RDM-Records Permissions Generators."""

import operator
from functools import reduce
from itertools import chain

from elasticsearch_dsl import Q, query
from flask_principal import UserNeed
from invenio_records_permissions.generators import Generator


class IfRestricted(Generator):
    """IfRestricted.

    IfRestricted(
        'record',
        then_=[RecordPermissionLevel('view')],
        else_=[ActionNeed(superuser-access)],
    )

    A record permission level defines an aggregated set of
    low-level permissions,
    that grants increasing level of permissions to a record.

    """

    def __init__(self, field, then_, else_):
        """Constructor."""
        self.field = field
        self.then_ = then_
        self.else_ = else_

    def generators(self, record):
        """Get the "then" or "else" generators."""
        is_restricted = getattr(
            record.access.protection, self.field, "restricted")
        return self.then_ if is_restricted == "restricted" else self.else_

    def needs(self, record=None, **kwargs):
        """Set of Needs granting permission."""
        needs = [
            g.needs(record=record, **kwargs) for g in self.generators(record)]
        return set(chain.from_iterable(needs))

    def excludes(self, record=None, **kwargs):
        """Set of Needs denying permission."""
        needs = [
            g.excludes(record=record, **kwargs) for g in self.generators(
                record)]
        return set(chain.from_iterable(needs))

    def make_query(self, status, generators, **kwargs):
        """Make a query for one set of generators."""
        q = Q("match", **{f"access.{self.field}": status})

        queries = [g.query_filter(**kwargs) for g in generators]
        queries = [q for q in queries if q]

        if queries:
            q &= reduce(operator.or_, queries)

        return q

    def query_filter(self, **kwargs):
        """Filters for current identity as super user."""
        q_restricted = self.make_query("restricted", self.then_, **kwargs)
        q_public = self.make_query("public", self.else_, **kwargs)
        return q_restricted | q_public


class RecordOwners(Generator):
    """Allows record owners."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs."""
        owners = record.access.owners.dump()
        return [UserNeed(owner.get('user')
                         ) for owner in owners]

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as owner."""
        for need in identity.provides:
            if need.method == 'id':
                return Q("term", **{"access.owned_by.user": need.value})
        return []
