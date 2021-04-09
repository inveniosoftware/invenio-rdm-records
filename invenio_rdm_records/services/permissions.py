# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permissions for Invenio RDM Records."""

from invenio_records_permissions.generators import AnyUser, \
    AuthenticatedUser, Disable, SystemProcess
from invenio_records_permissions.policies.records import RecordPermissionPolicy

from .generators import IfDraft, IfRestricted, RecordOwners, SecretLinks


class RDMRecordPermissionPolicy(RecordPermissionPolicy):
    """Access control configuration for records.

    Note that even if the array is empty, the invenio_access Permission class
    always adds the ``superuser-access``, so admins will always be allowed.

    - Create action given to everyone for now.
    - Read access given to everyone if public record and given to owners
      always. (inherited)
    - Update access given to record owners. (inherited)
    - Delete access given to admins only. (inherited)
    """

    NEED_LABEL_TO_ACTION = {
        'bucket-update': 'update_files',
        'bucket-read': 'read_files',
        'object-read': 'read_files',
    }

    # Records
    can_search = [AnyUser(), SystemProcess()]
    can_read = [
        IfRestricted('record', then_=[RecordOwners()], else_=[AnyUser()]),
        SystemProcess(),
        SecretLinks("read"),
    ]
    can_update = [Disable()]
    can_delete = [Disable()]

    # Drafts
    can_create = [AuthenticatedUser(), SystemProcess()]
    can_search_drafts = [AuthenticatedUser(), SystemProcess()]
    can_read_draft = [RecordOwners(), SystemProcess()]
    can_update_draft = [RecordOwners(), SystemProcess()]
    can_delete_draft = [RecordOwners(), SystemProcess()]

    can_manage = [RecordOwners(), SystemProcess()]
    can_new_version = [RecordOwners(), SystemProcess()]
    can_edit = [RecordOwners(), SystemProcess()]
    can_publish = [RecordOwners(), SystemProcess()]

    # Files
    # For now, can_read_files means:
    # - can list files
    # - can read a file metadata
    # - can download the file
    can_read_files = [
        IfRestricted(
            'files',
            then_=[RecordOwners()],
            else_=[
                IfDraft(
                    then_=[RecordOwners()],
                    else_=[AnyUser()]
                ),
            ]
        ),
        SystemProcess(),
        SecretLinks("read_files"),
    ]

    # Records - files
    can_create_files = [Disable()]
    # update_files is for updating files options
    can_update_files = [Disable()]
    can_delete_files = [Disable()]

    # Drafts - files
    # create_files is for 3-step file upload
    can_draft_create_files = [RecordOwners(), SystemProcess()]
    # update_files is for updating files options
    can_draft_update_files = [RecordOwners(), SystemProcess()]
    can_draft_delete_files = [RecordOwners(), SystemProcess()]
