# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""RDM user moderation action."""

from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.services.uow import TaskOp
from invenio_vocabularies.proxies import current_service

from ...proxies import current_rdm_records_service
from .tasks import (
    delete_record,
    restore_record,
    user_block_cleanup,
    user_restore_cleanup,
)
from .utils import get_user_records


def on_block(user_id, uow=None, **kwargs):
    """Removes records that belong to a user.

    Note: This function operates on all records of a user and thus has the potential
    to be a very heavy operation! Thus it should not be called as part of the handling
    of an HTTP request!
    """
    user_id = str(user_id)
    tombstone_data = {"note": "User was blocked"}

    # set the removal reason if the vocabulary item exists
    try:
        removal_reason_id = kwargs.get("removal_reason_id", "spam")
        vocab = current_service.read(
            identity=system_identity, id_=("removalreasons", removal_reason_id)
        )
        tombstone_data["removal_reason"] = {"id": vocab.id}
    except PIDDoesNotExistError:
        pass

    # soft-delete all the published records of that user
    for recid in get_user_records(user_id):
        uow.register(TaskOp(delete_record, recid=recid, tombstone_data=tombstone_data))

    # Send cleanup task to make sure all records are deleted
    uow.register(
        TaskOp.for_async_apply(
            user_block_cleanup,
            kwargs=dict(user_id=user_id, tombstone_data=tombstone_data),
            # wait for 10 minutes before starting the cleanup
            countdown=10 * 60,
        )
    )


def on_restore(user_id, uow=None, **kwargs):
    """Restores records that belong to a user.

    Note: This function operates on all records of a user and thus has the potential
    to be a very heavy operation! Thus it should not be called as part of the handling
    of an HTTP request!
    """
    user_id = str(user_id)

    # restore all the deleted records of that user
    for recid in get_user_records(user_id):
        uow.register(TaskOp(restore_record, recid=recid))

    # Send cleanup task to make sure all records are restored
    uow.register(
        TaskOp.for_async_apply(
            user_restore_cleanup,
            kwargs=dict(user_id=user_id),
            # wait for 10 minutes before starting the cleanup
            countdown=10 * 60,
        )
    )


def on_approve(user_id, uow=None, **kwargs):
    """Execute on user approve.

    Re-index user records and dump verified field into records.
    """
    from invenio_search.engine import dsl

    user_records_q = dsl.Q("term", **{"parent.access.owned_by.user": user_id})
    current_rdm_records_service.reindex_latest_first(
        identity=system_identity, extra_filter=user_records_q, uow=uow
    )
