# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""RDM user moderation action."""

from invenio_access.permissions import system_identity

from invenio_rdm_records.proxies import current_rdm_records_service


def on_block(user_id, uow=None, **kwargs):
    """Removes records that belong to a user."""
    pass


def on_restore(user_id, uow=None, **kwargs):
    """Restores records that belong to a user."""
    pass


def on_approve(user_id, **kwargs):
    """Execute on user approve.

    Re-index user records and dump verified field into records.
    """
    current_rdm_records_service.reindex_user_records(
        identity=system_identity, id_=user_id
    )
