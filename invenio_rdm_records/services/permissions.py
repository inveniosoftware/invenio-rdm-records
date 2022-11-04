# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permissions for Invenio RDM Records."""

from invenio_records_permissions.generators import (
    AnyUser,
    AuthenticatedUser,
    Disable,
    SystemProcess,
)
from invenio_records_permissions.policies.records import RecordPermissionPolicy

from .generators import (
    CommunityAction,
    IfFileIsLocal,
    IfRestricted,
    RecordOwners,
    SecretLinks,
    SubmissionReviewer,
)


class RDMRecordPermissionPolicy(RecordPermissionPolicy):
    """Access control configuration for records.

    Note that even if the array is empty, the invenio_access Permission class
    always adds the ``superuser-access``, so admins will always be allowed.
    """

    NEED_LABEL_TO_ACTION = {
        "bucket-update": "update_files",
        "bucket-read": "read_files",
        "object-read": "read_files",
    }

    #
    # High-level permissions (used by low-level)
    #
    can_manage = [
        RecordOwners(),
        CommunityAction("curate"),
        SystemProcess(),
    ]
    can_curate = can_manage + [SecretLinks("edit")]
    can_review = can_curate + [SubmissionReviewer()]
    can_preview = can_manage + [SecretLinks("preview"), SubmissionReviewer()]
    can_view = can_manage + [
        SecretLinks("view"),
        SubmissionReviewer(),
        CommunityAction("view"),
    ]

    can_authenticated = [AuthenticatedUser(), SystemProcess()]
    can_all = [AnyUser(), SystemProcess()]

    #
    #  Records
    #
    # Allow searching of records
    can_search = can_all

    # Allow reading metadata of a record
    can_read = [
        IfRestricted("record", then_=can_view, else_=can_all),
    ]
    # Allow reading the files of a record
    can_read_files = [
        IfRestricted("files", then_=can_view, else_=can_all),
    ]
    can_get_content_files = [
        # preview is same as read_files
        IfFileIsLocal(then_=can_preview, else_=[SystemProcess()])
    ]
    # Allow submitting new record
    can_create = can_authenticated

    #
    # Drafts
    #
    # Allow ability to search drafts
    can_search_drafts = can_authenticated
    # Allow reading metadata of a draft
    can_read_draft = can_preview
    # Allow reading files of a draft
    can_draft_read_files = can_preview
    # Allow updating metadata of a draft
    can_update_draft = can_review
    # Allow uploading, updating and deleting files in drafts
    can_draft_create_files = can_review
    can_draft_set_content_files = [
        # review is the same as create_files
        IfFileIsLocal(then_=can_review, else_=[SystemProcess()])
    ]
    can_draft_get_content_files = [
        # preview is same as read_files
        IfFileIsLocal(then_=can_preview, else_=[SystemProcess()])
    ]
    can_draft_commit_files = [
        # review is the same as create_files
        IfFileIsLocal(then_=can_review, else_=[SystemProcess()])
    ]
    can_draft_update_files = can_review
    can_draft_delete_files = can_review

    #
    # PIDs
    #
    can_pid_create = can_review
    can_pid_register = can_review
    can_pid_update = can_review
    can_pid_discard = can_review
    can_pid_delete = can_review

    #
    # Actions
    #
    # Allow to put a record in edit mode (create a draft from record)
    can_edit = can_curate
    # Allow deleting/discarding a draft and all associated files
    can_delete_draft = can_curate
    # Allow creating a new version of an existing published record.
    can_new_version = can_curate
    # Allow publishing a new record or changes to an existing record.
    can_publish = can_review
    # Allow lifting a record or draft.
    can_lift_embargo = can_manage

    #
    # Disabled actions (these should not be used or changed)
    #
    # - Records/files are updated/deleted via drafts so we don't support
    #   using below actions.
    can_update = [Disable()]
    can_delete = [Disable()]
    can_create_files = [Disable()]
    can_set_content_files = [Disable()]
    can_commit_files = [Disable()]
    can_update_files = [Disable()]
    can_delete_files = [Disable()]
