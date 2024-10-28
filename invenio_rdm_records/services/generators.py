# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-RDM-Records Permissions Generators."""

import operator
from collections import namedtuple
from functools import partial, reduce
from itertools import chain

from flask import g
from flask_principal import UserNeed
from invenio_communities.config import COMMUNITIES_ROLES
from invenio_communities.generators import CommunityRoleNeed, CommunityRoles
from invenio_communities.proxies import current_roles
from invenio_records_permissions.generators import ConditionalGenerator, Generator
from invenio_records_resources.services.files.transfer import TransferType
from invenio_search.engine import dsl

from ..records import RDMDraft
from ..records.systemfields.access.grants import Grant
from ..records.systemfields.deletion_status import RecordDeletionStatusEnum
from ..requests import CommunityInclusion
from ..requests.access import AccessRequestTokenNeed
from ..tokens.permissions import RATNeed

_Need = namedtuple("Need", ["method", "record"])

CommunityInclusionNeed = partial(_Need, "community-inclusion")
"""Defines a need for a community inclusion."""


class IfRestricted(ConditionalGenerator):
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
        super().__init__(then_, else_)

    def _condition(self, record, **kwargs):
        """Check if the record is restricted."""
        if record is None:
            # TODO - when permissions on links are checked, the record is not
            # passes properly, causing below ``record.access`` to fail.
            return False
        is_restricted = getattr(record.access.protection, self.field, "restricted")
        return is_restricted == "restricted"

    def query_filter(self, **kwargs):
        """Filters for current identity as super user."""
        q_restricted = dsl.Q("match", **{f"access.{self.field}": "restricted"})
        q_public = dsl.Q("match", **{f"access.{self.field}": "public"})
        then_query = self._make_query(self.then_, **kwargs)
        else_query = self._make_query(self.else_, **kwargs)

        if then_query and else_query:
            return (q_restricted & then_query) | (q_public & else_query)
        elif then_query:
            return (q_restricted & then_query) | q_public
        elif else_query:
            return q_public & else_query
        else:
            return q_public


class IfDraft(ConditionalGenerator):
    """Generator that depends on whether the record is a draft or not.

    IfDraft(
        then_=[...],
        else_=[...],
    )

    This might be a temporary hack or the way to go.
    """

    def _condition(self, record, **kwargs):
        """Check if the record is a draft."""
        return isinstance(record, RDMDraft)


class IfFileIsLocal(ConditionalGenerator):
    """Conditional generator for file storage class."""

    def _condition(self, record, file_key=None, **kwargs):
        """Check if the file is local."""
        is_file_local = True
        if file_key:
            file_record = record.files.get(file_key)
            # file_record __bool__ returns false for `if file_record`
            file = file_record.file if file_record is not None else None
            is_file_local = not file or file.storage_class == TransferType.LOCAL
        else:
            file_records = record.files.entries
            for file_record in file_records:
                file = file_record.file
                if file and file.storage_class != TransferType.LOCAL:
                    is_file_local = False
                    break

        return is_file_local


class IfNewRecord(ConditionalGenerator):
    """Conditional generator for cases where we have a new record/draft."""

    def _condition(self, record=None, **kwargs):
        """Check if there is a record."""
        return record is None


class IfExternalDOIRecord(ConditionalGenerator):
    """Conditional generator for external DOI records."""

    def _condition(self, record=None, **kwargs):
        """Check if the record has an external DOI."""
        return record.get("pids", {}).get("doi", {}).get("provider") == "external"


class IfDeleted(ConditionalGenerator):
    """Conditional generator for deleted records."""

    def _condition(self, record=None, **kwargs):
        """Check if the record is deleted."""
        try:
            return record.deletion_status.is_deleted

        except AttributeError:
            # if the record doesn't have the attribute, we assume it's not deleted
            return False


class IfRecordDeleted(Generator):
    """Custom conditional generator for deleted records."""

    def __init__(self, then_, else_):
        """Constructor."""
        self.then_ = then_
        self.else_ = else_

    def generators(self, record):
        """Get the "then" or "else" generators."""
        if record is None:
            # if no records, we assume it returns standard else response
            return self.else_

        is_deleted = record.deletion_status.is_deleted
        return self.then_ if is_deleted else self.else_

    def needs(self, record=None, **kwargs):
        """Set of Needs granting permission."""
        needs = [g.needs(record=record, **kwargs) for g in self.generators(record)]
        return set(chain.from_iterable(needs))

    def excludes(self, record=None, **kwargs):
        """Set of Needs denying permission."""
        needs = [g.excludes(record=record, **kwargs) for g in self.generators(record)]
        return set(chain.from_iterable(needs))

    def make_query(self, generators, **kwargs):
        """Make a query for one set of generators."""
        queries = [g.query_filter(**kwargs) for g in generators]
        queries = [q for q in queries if q]
        return reduce(operator.or_, queries) if queries else None

    def query_filter(self, **kwargs):
        """Filters for current identity."""
        q_then = dsl.Q("match_all")
        q_else = dsl.Q(
            "term", **{"deletion_status": RecordDeletionStatusEnum.PUBLISHED.value}
        )
        then_query = self.make_query(self.then_, **kwargs)
        else_query = self.make_query(self.else_, **kwargs)

        if then_query and else_query:
            return (q_then & then_query) | (q_else & else_query)
        elif then_query:
            return (q_then & then_query) | q_else
        elif else_query:
            return q_else & else_query
        else:
            return q_else


class RecordOwners(Generator):
    """Allows record owners."""

    def needs(self, record=None, **kwargs):
        """Enabling Needs."""
        if record is None:
            # 'record' is required, so if not passed we default to empty array,
            # i.e. superuser-access.
            return []

        return [UserNeed(record.parent.access.owner.owner_id)]

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as owner."""
        users = [n.value for n in identity.provides if n.method == "id"]
        if users:
            return dsl.Q("terms", **{"parent.access.owned_by.user": users})


class AccessGrant(Generator):
    """Allows access according to the given access grants."""

    def __init__(self, permission):
        """Constructor."""
        self._permission = permission

    def needs(self, record=None, **kwargs):
        """Enabling needs."""
        if record is None:
            return []

        return record.parent.access.grants.needs(self._permission)

    def _make_grant_token(self, subj_type, subj_id):
        """Create a grant token from the specified parts."""
        # NOTE: `Grant.to_token()` doesn't need the actual subject to be set
        return Grant(
            subject=None,
            origin=None,
            permission=self._permission,
            subject_type=subj_type,
            subject_id=subj_id,
        ).to_token()

    def _grant_tokens(self, identity):
        """Parse a list of grant tokens provided by the given identity."""
        tokens = []
        for need in identity.provides:
            token = None
            if need.method == "id":
                token = self._make_grant_token("user", need.value)
            elif need.method == "role":
                token = self._make_grant_token("role", need.value)
            elif need.method == "system_role":
                token = self._make_grant_token("system_role", need.value)

            if token is not None:
                tokens.append(token)

        return tokens

    def query_filter(self, identity=None, **kwargs):
        """Filters for the current identity in access grants."""
        if identity is not None:
            tokens = self._grant_tokens(identity)
            if tokens:
                return dsl.Q("terms", **{"parent.access.grant_tokens": tokens})

        return []


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
        secret_links = [n.value for n in identity.provides if n.method == "link"]

        if secret_links:
            return dsl.Q("terms", **{"parent.access.links.id": secret_links})


class SubmissionReviewer(Generator):
    """Roles for community's reviewers."""

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


class CommunityInclusionReviewers(Generator):
    """Needs for community members that have rights to curate the record of the inclusion-requests.

    WARNING: This is a TEMPORAL solution, meaning that it should not be reused around. This need is used to grant a
    "one time" ticket to access a concrete view (in this case the community inclusion request details page of restricted
    records).
    """

    def needs(self, record=None, **kwargs):
        """Set of Needs granting permission."""
        if record is not None:
            return [CommunityInclusionNeed(record.pid.pid_value)]
        return []


class RecordCommunitiesAction(CommunityRoles):
    """Roles generators of all record's communities for a given member's action."""

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
            if n.method == "community" and n.role in roles:
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
        return dsl.Q("terms", **{"parent.communities.ids": self.communities(identity)})


class ResourceAccessToken(Generator):
    """Allow resource access tokens."""

    def __init__(self, access):
        """Constructor."""
        self.access = access

    def needs(self, record=None, file_key=None, **kwargs):
        """Enabling Needs."""
        record_owner = record.parent.access.owner

        if record_owner and record and file_key:
            signer_id = record_owner.owner_id
            return [RATNeed(signer_id, record["id"], file_key, self.access)]

        return []


class IfCreate(ConditionalGenerator):
    """Check if the request is created or modified."""

    def _condition(self, record=None, request=None, **kwargs):
        """Check if record is empty - meaning it is created for the first time ."""
        return record is None and request is None


class IfRequestType(ConditionalGenerator):
    """Conditional generator for requests of a certain type."""

    def __init__(self, request_type, then_, else_):
        """Constructor."""
        self.request_type = request_type
        super().__init__(then_, else_)

    def _condition(self, request=None, **kwargs):
        """Check if the request type matches the configured one."""
        if request is not None:
            return isinstance(request.type, self.request_type)

        return False


class GuestAccessRequestToken(Generator):
    """Require a ``AccessRequestTokenNeed(request['payload']['token'])``."""

    def needs(self, request=None, **kwargs):
        """Require a ``AccessRequestTokenNeed(request['payload']['token'])``."""
        if request is not None:
            return [AccessRequestTokenNeed(request["payload"]["token"])]

        return []


class IfOneCommunity(ConditionalGenerator):
    """Conditional generator for records always in communities case."""

    def _condition(self, record=None, **kwargs):
        """Check if the record is associated with one community."""
        return bool(record and len(record.parent.communities.ids) == 1)


class IfAtLeastOneCommunity(ConditionalGenerator):
    """Conditional generator for records always in communities case."""

    def _condition(self, record=None, **kwargs):
        """Check if the record is associated with at least one community."""
        return bool(record and record.parent.communities.ids)
