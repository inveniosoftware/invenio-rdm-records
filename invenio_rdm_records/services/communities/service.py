# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Communities Service."""
from invenio_records_resources.services import (
    RecordIndexerMixin,
    Service,
    ServiceSchemaWrapper,
)
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    RecordIndexOp,
    unit_of_work,
)

from invenio_rdm_records.services.errors import RecordCommunityMissing


class RecordCommunitiesService(Service, RecordIndexerMixin):
    """Record communities service.

    The communities service is in charge of managing communities of a given record.
    """

    @property
    def schema(self):
        """Returns the data schema instance."""
        return ServiceSchemaWrapper(self, schema=self.config.schema)

    @property
    def record_cls(self):
        """Factory for creating a record class."""
        return self.config.record_cls

    @unit_of_work()
    def create(self, identity, data, record, uow=None):
        """Include the record in the given communities."""
        pass

    def _remove(self, community_id, record):
        """Remove a community from the record."""
        if community_id not in record.parent.communities.ids:
            raise RecordCommunityMissing(record.id, community_id)

        # Default community is deleted when the exact same community is removed from the record
        record.parent.communities.remove(community_id)

    @unit_of_work()
    def delete(self, identity, record_id, data, revision_id=None, uow=None):
        """Remove communities from the record."""
        record = self.record_cls.pid.resolve(record_id)
        self.require_permission(identity, "delete_community", record=record)

        valid_data, errors = self.schema.load(
            data,
            context={
                "identity": identity,
                "max_number": self.config.max_number_of_removals,
            },
            raise_errors=True,
        )
        communities = valid_data["communities"]

        for community in communities:
            community_id = community["id"]
            try:
                self._remove(community_id, record)
                uow.register(RecordCommitOp(record.parent))
                uow.register(RecordIndexOp(record, indexer=self.indexer))
            except RecordCommunityMissing:
                errors.append(
                    {
                        "community": community_id,
                        "message": f"The record {record_id} does not belong to the community {community_id}",
                    }
                )

        return errors
