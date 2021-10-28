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
from marshmallow import ValidationError

from ...proxies import current_rdm_records
from ..pids.tasks import register_pid, update_pid


class PIDsComponent(ServiceComponent):
    """Service component for pids."""

    # hook methods
    def create(self, identity, data=None, record=None, errors=None):
        """This method is called on draft creation.

        It should validate and add the pids to the draft.
        """
        # cant use or cuz [] is false
        errors = [] if errors is None else errors
        pids = self.service.pids.pid_manager.validate(
            data.get('pids', {}), record, errors
        )
        record.pids = pids  # the record is a draft

    def new_version(self, identity, draft=None, record=None):
        """A new draft should not have any pids from the previous record."""
        draft.pids = {}

    def publish(self, identity, draft=None, record=None):
        """Publish handler."""
        errors = []
        pids = self.service.pids.pid_manager.validate(
            draft.get('pids', {}), record, errors
        )
        if errors:
            raise ValidationError(message=errors)

        # Internally the following is done by the PIDs service
        #
        #            |      value     |   no value     |
        # |----------|----------------|----------------|
        # | managed  |     reserve    | create+reserve |
        # |----------|----------------|----------------|
        # | external | create+reserve |      fail      |
        # |----------|------- --------|----------------|

        # TODO: check creation of required exernal without value
        pids = self.service.pids.pid_manager.create_many(draft, pids)
        pids = {
            **pids,
            **self.service.pids.pid_manager.create_many_by_scheme(
                draft, self.service.config.pids_required
            )
        }
        self.service.pids.pid_manager.reserve_many(draft, pids)

        record.pids = pids

    # the delete hook is not implemented because record deletion is
    # forbidden by permissions. In addition, the flow to when/how delete a
    # reserved/registered pid is not trivial. It is dealt with by the
    # inactivate function at pids service level
    def delete_draft(self, identity, draft=None, record=None, force=False):
        """This method deletes PIDs of a draft.

        It should only delete pids with status `NEW`, other pids would
        belong to previous versions of the record.
        """
        # FIXME: per pid permissions like in update, now no perm check
        self.service.pids.pid_manager.discard_all(draft.pids)
        draft.pids = {}

    def update_draft(self, identity, data=None, record=None, errors=None):
        """Update draft handler.

        The permission check is performed on pid updates, no new additions.
        In addition, they check only if it is allowed to remove the pid
        since adding a new one has the same restrictions than the record
        update.
        """
        errors = [] if errors is None else errors
        pids = self.service.pids.pid_manager.validate(
            data.get('pids', {}), record, errors
        )
        # FIXME: permissions check? global? it is done at pidsservice not manager
        pids = self.service.pids.pid_manager.update(record, pids)

        record.pids = pids

    def edit(self, identity, draft=None, record=None):
        """Add current pids from the record to the draft.

        PIDS are taken from the published record so that cannot be changed in
        the draft.
        """
        # errors are not used because we do not want to fail on create
        pids = self.service.pids.pid_manager.validate(
            record.get('pids', {}), record
        )
        draft.pids = pids

    def post_publish(self, identity, record=None, is_published=False):
        """Post publish handler."""
        # no need to validate since it was published already
        for scheme in record.get('pids', {}).keys():
            if is_published:
                update_pid.delay(record["id"], scheme)
            else:
                register_pid.delay(record["id"], scheme)
