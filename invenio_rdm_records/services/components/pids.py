# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM service component for pids."""

from invenio_drafts_resources.services.records.components import \
    ServiceComponent
from invenio_records_resources.services.uow import TaskOp

from ..pids.tasks import register_pid, update_pid


class PIDsComponent(ServiceComponent):
    """Service component for pids."""

    # hook methods
    def create(self, identity, data=None, record=None, errors=None):
        """This method is called on draft creation.

        It should validate and add the pids to the draft.
        """
        pids = data.get('pids', {})
        self.service.pids.pid_manager.validate(pids, record, errors)
        record.pids = pids

    def new_version(self, identity, draft=None, record=None):
        """A new draft should not have any pids from the previous record."""
        draft.pids = {}

    def publish(self, identity, draft=None, record=None):
        """Publish handler."""
        new_pids = draft.get('pids', {})
        self.service.pids.pid_manager.validate(
           new_pids, record, raise_errors=True
        )

        # Internally the following is done by the PIDs service
        #
        #            |      value     |   no value     |
        # |----------|----------------|----------------|
        # | managed  |     reserve    | create+reserve |
        # |----------|----------------|----------------|
        # | external | create+reserve |      fail      |
        # |----------|------- --------|----------------|

        old_pids = dict(record.get('pids', {}))  # force copy
        new_schemes = set(new_pids.keys())
        old_schemes = set(old_pids.keys())

        remove_schemes = new_schemes.intersection(old_schemes)
        for scheme in remove_schemes:
            old_id = old_pids[scheme]["identifier"]
            new_id = new_pids[scheme]["identifier"]
            if old_id == new_id:
                old_pids.pop(scheme)  # no need for removal

        self.service.pids.pid_manager.discard_all(old_pids)

        required_schemes = \
            set(self.service.config.pids_required) - old_schemes - new_schemes
        pids = {
            **self.service.pids.pid_manager.create_all(draft, new_pids),
            **self.service.pids.pid_manager.create_all(draft, required_schemes)
        }

        self.service.pids.pid_manager.reserve_all(draft, pids)

        record.pids = pids

        # Run register/update tasks after transaction commit.
        for scheme in pids.keys():
            if draft.is_published:
                self.uow.register(TaskOp(update_pid, record["id"], scheme))
            else:
                self.uow.register(TaskOp(register_pid, record["id"], scheme))

    # the delete hook is not implemented because record deletion is
    # forbidden by permissions. In addition, the flow to when/how delete a
    # reserved/registered pid is not trivial. It is dealt with by the
    # inactivate function at pids service level
    def delete_draft(self, identity, draft=None, record=None, force=False):
        """This method deletes PIDs of a draft.

        It should only delete pids with status `NEW`, other pids would
        belong to previous versions of the record.
        """
        to_remove = dict(draft.get('pids', {}))  # force copy
        old_pids = record.get('pids', {}).keys() if record else []
        for scheme in old_pids:
            to_remove.pop(scheme)

        self.service.pids.pid_manager.discard_all(to_remove)
        draft.pids = {}

    def update_draft(self, identity, data=None, record=None, errors=None):
        """Update draft handler."""
        pids = data.get('pids', {})
        self.service.pids.pid_manager.validate(pids, record, errors)
        record.pids = pids

    def edit(self, identity, draft=None, record=None):
        """Add current pids from the record to the draft.

        PIDS are taken from the published record so that cannot be changed in
        the draft.
        """
        pids = record.get('pids', {})
        self.service.pids.pid_manager.validate(pids, record)
        draft.pids = pids
