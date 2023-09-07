# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""RDM user moderation action."""

from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_vocabularies.proxies import current_service

from ...proxies import current_rdm_records_service
from ...records.systemfields.deletion_status import RecordDeletionStatusEnum


def _get_records_for_user(user_id):
    """Helper function for getting all the records of the user.

    Note: This function performs DB queries yielding all records for a given
    user (which is not hard-limited in the system) and performs service calls
    on each of them. Thus, this function has the potential of being a very
    heavy operation, and should not be called as part of the handling of an
    HTTP request!
    """
    record_cls = current_rdm_records_service.record_cls
    model_cls = record_cls.model_cls
    parent_cls = record_cls.parent_record_cls
    parent_model_cls = parent_cls.model_cls

    # get all the parent records owned by the blocked user
    parent_recs = [
        parent_cls(m.data, model=m)
        for m in parent_model_cls.query.filter(
            parent_model_cls.json["access"]["owned_by"]["user"].as_string() == user_id
        ).all()
    ]

    # get all child records of the chosen parent records
    recs = [
        record_cls(m.data, model=m)
        for m in model_cls.query.filter(
            model_cls.parent_id.in_([p.id for p in parent_recs])
        ).all()
    ]

    return recs


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
        removal_reason_id = kwargs.get("removal_reason_id", "misconduct")
        vocab = current_service.read(
            identity=system_identity, id_=("removalreasons", removal_reason_id)
        )
        tombstone_data["removal_reason"] = {"id": vocab.id}
    except PIDDoesNotExistError:
        pass

    # soft-delete all the published records of that user
    for rec in _get_records_for_user(user_id):
        if not rec.deletion_status.is_deleted:
            current_rdm_records_service.delete_record(
                system_identity,
                rec.pid.pid_value,
                tombstone_data,
                uow=uow,
            )


def on_restore(user_id, uow=None, **kwargs):
    """Restores records that belong to a user.

    Note: This function operates on all records of a user and thus has the potential
    to be a very heavy operation! Thus it should not be called as part of the handling
    of an HTTP request!
    """
    user_id = str(user_id)

    # restore all the deleted records of that user
    for rec in _get_records_for_user(user_id):
        if rec.deletion_status == RecordDeletionStatusEnum.DELETED:
            current_rdm_records_service.restore_record(
                system_identity,
                rec.pid.pid_value,
                uow=uow,
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
