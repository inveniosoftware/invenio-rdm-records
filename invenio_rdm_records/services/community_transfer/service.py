# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Community transfer service."""

from invenio_search.engine import dsl
from invenio_rdm_records.proxies import current_rdm_records_service as records_service
from invenio_communities.proxies import current_communities
from invenio_drafts_resources.services.records.uow import (
    ParentRecordCommitOp,
    RecordCommitOp,
)
from werkzeug.local import LocalProxy
from invenio_records_resources.services.uow import unit_of_work


community_service = LocalProxy(lambda: current_communities.service)


def _all_records_q(community_ids):
    """Auxiliary function that creates a query to filter records by community ids.

    Fetches the latest versions of the records only.

    :param community_ids: The list of community ids to filter the records by.
    """
    extra_filter = dsl.query.Bool(
        "must",
        must=[
            dsl.Q("terms", **{"parent.communities.ids": community_ids}),
            dsl.Q("term", **{"versions.is_latest": True}),
        ],
    )

    return extra_filter


class CommunityTransferService:
    """Service for transferring communities and records to new parents."""

    @unit_of_work()
    def transfer_to_new_parent(
        self,
        identity,
        comm_slugs,
        new_parent,
        records_q=None,
        set_default=False,
        uow=None,
    ):
        """
        Transfers communities to a new parent and update the records accordingly.

        This is done in two steps:
        1. Move the communities to the new parent.
        2. Move the records to the new parent.

        By default, all records of the community will be moved to the target community. This can be modified by
        providing a query to filter the records to be moved.

        :param list comm_slugs: The slugs of the communities to be moved.
        :param str new_parent: The slug of the target community where the communities will be moved to.
        :param Query records_q: The query to filter the records to be moved. If not provided, all records
            of the community will be moved.
        :param bool set_default: Flag indicating whether to set the target community as the default community for the
            records being moved.
        :param UnitOfWork uow: The unit of work to use for the database operations. If not provided, a new
            unit of work will be created.
        :return: None
        :rtype: None
        """
        t_comm = community_service.read(identity, new_parent)
        c_ids = []
        # Step 1 - move communities to new target
        for c_slug in comm_slugs:
            c_comm = community_service.read(identity, c_slug)
            self._add_parent_to_community(
                identity, community=c_comm, parent=t_comm, uow=uow
            )
            c_ids.append(c_comm.id)

        # Step 2 - move records to new parent
        if not records_q:
            records_q = _all_records_q(c_ids)
        records = self.search_records(identity, records_q)
        self.add_records_to_community(
            identity, records, new_parent, set_default=set_default, uow=uow
        )

    def _include_one_record(self, record, community, set_default=False, uow=None):
        """Includes a record in a community.

        It bypasses the inclusion request and directly adds the record to the community.

        :param record: The record to be included.
        :param community: The community to include the record in.
        :param set_default: Flag indicating whether to set the included record as the default.
        :param uow: The unit of work to register the operations with.
        """
        # Check permissions
        # Add record to community
        default = set_default or not record.parent.communities
        req = None
        record.parent.communities.add(community, request=req, default=default)

        parent_community = getattr(community, "parent", None)
        already_in_parent = parent_community and str(parent_community.id) in record

        if parent_community and not already_in_parent:
            record.parent.communities.add(parent_community, request=req)

        # Commit parent, re-index record and parent
        uow.register(
            ParentRecordCommitOp(
                record.parent, indexer_context=dict(service=records_service)
            )
        )
        uow.register(
            RecordCommitOp(record, indexer=records_service.indexer, index_refresh=True)
        )

    # Add records to community in bulk
    def add_records_to_community(
        self, identity, ids, comm_slug, set_default=False, uow=None
    ):
        """
        Add records to a community.

        :param ids: The list of record IDs to add to the community.
        :param comm_slug: The slug of the community to add the records to.
        :param set_default: Whether to set the added records as the default records for the community. Default is False.
        :param uow: Optional unit of work object for database operations.
        :return: None
        """
        # Check permissions
        for record_id in ids:
            record = records_service.read(identity, record_id)
            c_comm = community_service.read(identity, comm_slug)
            self._include_one_record(
                record._record, c_comm._record, set_default=set_default, uow=uow
            )

    def search_records(self, identity, records_q):
        """Creates a search object for records and returns the record ids using a scan() query."""
        search = records_service.create_search(
            identity,
            records_service.record_cls,
            records_service.config.search,
            permission_action="read",
            extra_filter=records_q,
        )

        yield from map(lambda x: x.id, search.scan())

    def _add_parent_to_community(self, identity, community, parent, uow=None):
        """
        Adds a parent to a community.

        :param community: The community to which the parent will be added.
        :param parent: The parent to be added to the community.
        :param uow: Optional unit of work object for database operations.
        :return: The result of the community update operation.
        """

        # Prepare parent to allow children, just in case
        community_service.update(
            identity=identity,
            id_=str(parent.id),
            data={**parent.data, "children": {"allow": True}},
        )
        # Add community to parent
        res = community_service.update(
            identity,
            str(community.id),
            {**community.data, "parent": {"id": parent.id}},
            uow=uow,
        )
        return res
