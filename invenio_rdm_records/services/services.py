# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2023 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2022 Universität Hamburg.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service."""


import arrow
from invenio_drafts_resources.services.records import RecordService
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work
from invenio_requests.services.results import EntityResolverExpandableField

from invenio_rdm_records.services.errors import EmbargoNotLiftedError
from invenio_rdm_records.services.results import ParentCommunitiesExpandableField


class RDMRecordService(RecordService):
    """RDM record service."""

    def __init__(
        self,
        config,
        files_service=None,
        draft_files_service=None,
        access_service=None,
        pids_service=None,
        review_service=None,
    ):
        """Constructor for RecordService."""
        super().__init__(config, files_service, draft_files_service)
        self._access = access_service
        self._pids = pids_service
        self._review = review_service

    #
    # Subservices
    #
    @property
    def access(self):
        """Record access service."""
        return self._access

    @property
    def pids(self):
        """Record PIDs service."""
        return self._pids

    @property
    def review(self):
        """Record review service."""
        return self._review

    #
    # Properties
    #
    @property
    def expandable_fields(self):
        """Get expandable fields.

        Expand community field to return community details.
        """
        return [
            EntityResolverExpandableField("parent.review.receiver"),
            ParentCommunitiesExpandableField("parent.communities.default"),
        ]

    #
    # Service methods
    #
    @unit_of_work()
    def lift_embargo(self, identity, _id, uow=None):
        """Lifts embargo from the record and draft (if exists).

        It's an error if you try to lift an embargo that has not yet expired.
        Use this method in combination with scan_expired_embargos().
        """
        # Get the record
        record = self.record_cls.pid.resolve(_id)

        # Check permissions
        self.require_permission(identity, "lift_embargo", record=record)

        # Modify draft embargo if draft exists and it's the same as the record.
        draft = None
        if record.has_draft:
            draft = self.draft_cls.pid.resolve(_id, registered_only=False)
            if record.access == draft.access:
                if not draft.access.lift_embargo():
                    raise EmbargoNotLiftedError(_id)
                uow.register(RecordCommitOp(draft, indexer=self.indexer))

        if not record.access.lift_embargo():
            raise EmbargoNotLiftedError(_id)

        uow.register(RecordCommitOp(record, indexer=self.indexer))

    def scan_expired_embargos(self, identity):
        """Scan for records with an expired embargo."""
        today = arrow.utcnow().date().isoformat()

        embargoed_q = (
            f"access.embargo.active:true AND access.embargo.until:[* TO {today}]"
        )

        return self.scan(identity=identity, q=embargoed_q)

    def oai_result_item(self, identity, oai_record_source):
        """Get a result item from a record source in the OAI server.

        This function is ONLY intended to be used by the OAI-PMH server because
        the OAIServer does not use the service directly to retrieve records.
        The OAIServer predates the software architecture and thus to avoid
        rewriting it, we allow exceptions to get data from the search index
        and pass it into the service (normally the service must be responsible
        for this).
        """
        record = self.record_cls.loads(oai_record_source)
        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )
