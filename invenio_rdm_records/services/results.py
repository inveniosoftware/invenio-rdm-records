# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
# Copyright (C) 2023 TU Wien.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Service results."""

from invenio_communities.communities.entity_resolvers import pick_fields
from invenio_communities.communities.schema import CommunityGhostSchema
from invenio_communities.proxies import current_communities
from invenio_records_resources.services.base.results import (
    ServiceItemResult,
    ServiceListResult,
)
from invenio_records_resources.services.records.results import (
    ExpandableField,
    RecordList,
)
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


class RDMRecordList(RecordList):
    """Record list with custom fields."""

    @property
    def hits(self):
        """Iterator over the hits."""
        for hit in self._results:
            # Load dump
            record_dict = hit.to_dict()

            index_name = self._service.record_cls.index._name
            if index_name in hit.meta["index"]:
                record = self._service.record_cls.loads(record_dict)
            else:
                record = self._service.draft_cls.loads(record_dict)

            # Project the record
            projection = self._schema.dump(
                record,
                context=dict(
                    identity=self._identity,
                    record=record,
                    meta=hit.meta,
                ),
            )
            if self._links_item_tpl:
                projection["links"] = self._links_item_tpl.expand(
                    self._identity, record
                )

            yield projection


class RDMRecordRevisionsList(ServiceListResult):
    """Record revisions list.

    We need a custom result class to handle the record revisions list as they are stored only in DB.
    """

    def __init__(self, identity, revisions):
        """Instantiate a Collection tree list item."""
        self._identity = identity
        self._revisions = revisions

    def to_dict(self):
        """Serialize the collection tree list to a dictionary."""
        res = map(
            lambda revision: {
                "updated": revision.updated,
                "created": revision.created,
                "revision_id": revision.transaction_id,
                "json": revision.json,
            },
            self._revisions,
        )
        return list(res)

    def __iter__(self):
        """Iterate over the collection revisions."""
        return iter(self._revisions)
