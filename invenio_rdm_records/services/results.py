# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Service results."""

from invenio_communities.communities.entity_resolvers import pick_fields
from invenio_communities.communities.schema import CommunityGhostSchema
from invenio_communities.proxies import current_communities
from invenio_records_resources.services.records.results import ExpandableField
from invenio_users_resources.proxies import current_user_resources

from .dummy import DummyExpandingService


class ParentCommunitiesExpandableField(ExpandableField):
    """Parent communities field."""

    def ghost_record(self, value):
        """Return tombstone representation of not resolved community."""
        return CommunityGhostSchema().dump(value)

    def system_record(self):
        """Override default."""
        raise NotImplementedError()

    def get_value_service(self, value):
        """Return the value and the service via entity resolvers."""
        return value, current_communities.service

    def pick(self, identity, resolved_rec):
        """Pick fields defined in the entity resolver."""
        return pick_fields(identity, resolved_rec)


class GrantSubjectExpandableField(ExpandableField):
    """Expandable field for user-type grant subjects."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super().__init__(*args, **kwargs)
        self._system_roles_service = DummyExpandingService("system_role")

    def ghost_record(self, value):
        """Return tombstone representation of the grant subject."""
        return value

    def system_record(self):
        """Override default."""
        raise NotImplementedError()

    def get_value_service(self, value):
        """Get the service associated with the given value."""
        svc = None

        if value["type"] == "user":
            svc = current_user_resources.users_service
        elif value["type"] == "role":
            svc = current_user_resources.groups_service
        elif value["type"] == "system_role":
            svc = self._system_roles_service

        return value["id"], svc

    def pick(self, identity, resolved_rec):
        """Pick fields defined in the entity resolver."""
        return resolved_rec
