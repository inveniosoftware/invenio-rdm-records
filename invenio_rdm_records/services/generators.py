# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-RDM-Records Permissions Generators."""

import operator
from functools import reduce
from itertools import chain

from elasticsearch_dsl import Q
from flask_principal import UserNeed
from invenio_access.permissions import authenticated_user
from invenio_communities.generators import CommunityRoleNeed, CommunityRoles
from invenio_communities.proxies import current_roles
from invenio_records_permissions.generators import Generator

from invenio_rdm_records.records import RDMDraft


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
        if record is None:
            # TODO - when permissions on links are checked, the record is not
            # passes properly, causing below ``record.access`` to fail.
            return self.else_
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

    def make_query(self, generators, **kwargs):
        """Make a query for one set of generators."""
        queries = [g.query_filter(**kwargs) for g in generators]
        queries = [q for q in queries if q]
        return reduce(operator.or_, queries) if queries else None

    def query_filter(self, **kwargs):
        """Filters for current identity as super user."""
        q_restricted = Q("match", **{f"access.{self.field}": "restricted"})
        q_public = Q("match", **{f"access.{self.field}": "public"})
        then_query = self.make_query(self.then_, **kwargs)
        else_query = self.make_query(self.else_, **kwargs)

        if then_query and else_query:
            return (q_restricted & then_query) | (q_public & else_query)
        elif then_query:
            return (q_restricted & then_query) | q_public
        elif else_query:
            return q_public & else_query
        else:
            return q_public


class RecordOwners(Generator):
    """Allows record owners."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs."""
        if record is None:
            # 'record is None' means that this must be a 'create'
            # this should be allowed for any authenticated user
            return [authenticated_user]

        return [
            UserNeed(owner.owner_id) for owner in record.parent.access.owners
        ]

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as owner."""
        users = [n.value for n in identity.provides if n.method == "id"]
        if users:
            return Q("terms", **{"parent.access.owned_by.user": users})


class IfDraft(Generator):
    """Generator that depends on whether the record is a draft or not.

    IfDraft(
        then_=[...],
        else_=[...],
    )

    This might be a temporary hack or the way to go.
    """

    def __init__(self, then_, else_):
        """Constructor."""
        self.then_ = then_
        self.else_ = else_

    def _generators(self, record):
        """Get the "then" or "else" generators."""
        return self.then_ if isinstance(record, RDMDraft) else self.else_

    def needs(self, record=None, **kwargs):
        """Set of Needs granting permission."""
        return list(set(chain.from_iterable(
            [
                g.needs(record=record, **kwargs)
                for g in self._generators(record)
            ]
        )))

    def excludes(self, record=None, **kwargs):
        """Set of Needs denying permission."""
        return list(set(chain.from_iterable(
            [
                g.excludes(record=record, **kwargs)
                for g in self._generators(record)
            ]
        )))


class SecretLinks(Generator):
    """Secret Links for records."""

    def __init__(self, permission):
        """Constructor."""
        self.permission = permission

    def needs(self, record=None, **kwargs):
        """Set of Needs granting permission."""
        if record is None:
            return []

        return record.parent.access.links.needs(self.permission)

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity secret links."""
        secret_links = [
            n.value for n in identity.provides if n.method == "link"
        ]

        if secret_links:
            return Q("terms", **{"parent.access.links.id": secret_links})


class SubmissionReviewer(Generator):
    """Curators for community submission requests."""

    def needs(self, record=None, **kwargs):
        """Set of Needs granting permission."""
        if record is None or record.parent.review is None:
            return []

        # we only expect submission review requests here
        # and as such, we expect the receiver to be a community
        # and the topic to be a record
        request = record.parent.review
        receiver = request.receiver
        if receiver is not None:
            return receiver.get_needs(ctx=request.type.needs_context)
        return []


class CommunityAction(CommunityRoles):
    """Member of a community with a given action."""

    def __init__(self, action):
        """Initialize generator."""
        self._action = action

    def roles(self, **kwargs):
        """Roles for a given action."""
        return {r.name for r in current_roles.can(self._action)}

    def communities(self, identity):
        """Communities that an identity can manage."""
        roles = self.roles()
        community_ids = set()
        for n in identity.provides:
            if n.method == 'community' and n.role in roles:
                community_ids.add(n.value)
        return list(community_ids)

    def needs(self, record=None, **kwargs):
        """Set of Needs granting permission."""
        if record is None:
            return []

        _needs = set()
        for c in record.parent.communities.ids:
            for role in self.roles(**kwargs):
                _needs.add(CommunityRoleNeed(c, role))
        return _needs

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as member."""
        return Q(
            "terms",
            **{"parent.communities.ids": self.communities(identity)}
        )
