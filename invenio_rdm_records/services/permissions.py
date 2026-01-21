# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019 Northwestern University.
# Copyright (C) 2023 TU Wien.
# Copyright (C) 2024 CESNET.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permissions for Invenio RDM Records."""

from invenio_administration.generators import Administration
from invenio_communities.generators import CommunityCurators
from invenio_records_permissions.generators import (
    AnyUser,
    AuthenticatedUser,
    Disable,
    IfConfig,
    SystemProcess,
)
from invenio_records_permissions.policies.records import RecordPermissionPolicy
from invenio_records_resources.services.files.generators import IfTransferType
from invenio_records_resources.services.files.transfer import (
    LOCAL_TRANSFER_TYPE,
    MULTIPART_TRANSFER_TYPE,
)
from invenio_requests.services.generators import IfLocked, Receiver, Status
from invenio_requests.services.permissions import (
    PermissionPolicy as RequestPermissionPolicy,
)
from invenio_users_resources.services.permissions import UserManager

from ..requests.access import GuestAccessRequest
from .generators import (
    AccessGrant,
    CommunityInclusionReviewers,
    GuestAccessRequestToken,
    IfAtLeastOneCommunity,
    IfCreate,
    IfDeleted,
    IfExternalDOIRecord,
    IfNewRecord,
    IfOneCommunity,
    IfRecordDeleted,
    IfRequestType,
    IfRestricted,
    RecordCommunitiesAction,
    RecordOwners,
    RequestReviewers,
    ResourceAccessToken,
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

    # permission meant for global curators of the instance
    # (for now applies to internal notes field only
    # to be replaced with an adequate permission when it is defined)
    can_manage_internal = [SystemProcess()]
    #
    # High-level permissions (used by low-level)
    #
    can_manage = [
        RecordOwners(),
        RecordCommunitiesAction("curate"),
        AccessGrant("manage"),
        SystemProcess(),
    ]
    can_curate = can_manage + [AccessGrant("edit"), SecretLinks("edit")]
    can_review = can_curate + [SubmissionReviewer()]
    can_preview = can_curate + [
        AccessGrant("preview"),
        SecretLinks("preview"),
        SubmissionReviewer(),
        RequestReviewers(),
        UserManager,
    ]
    can_view = can_preview + [
        AccessGrant("view"),
        SecretLinks("view"),
        SubmissionReviewer(),
        CommunityInclusionReviewers(),
        RecordCommunitiesAction("view"),
    ]

    can_authenticated = [AuthenticatedUser(), SystemProcess()]
    can_all = [AnyUser(), SystemProcess()]

    #
    # Miscellaneous
    #
    # Allow for querying of statistics
    # - This is currently disabled because it's not needed and could potentially
    #   open up surface for denial of service attacks
    can_query_stats = [Disable()]

    #
    #  Records
    #
    # Allow searching of records
    can_search = can_all

    # Allow reading metadata of a record
    can_read = [
        IfRestricted("record", then_=can_view, else_=can_all),
    ]

    # Used for search filtering of deleted records
    # cannot be implemented inside can_read - otherwise permission will
    # kick in before tombstone renders
    can_read_deleted = [
        IfRecordDeleted(
            then_=[UserManager, SystemProcess()],
            else_=can_read,
        )
    ]
    can_read_deleted_files = can_read_deleted
    can_media_read_deleted_files = can_read_deleted_files
    # Allow reading the files of a record
    can_read_files = [
        IfRestricted("files", then_=can_view, else_=can_all),
        ResourceAccessToken("read"),
    ]
    can_get_content_files = [
        # note: even though this is closer to business logic than permissions,
        # it was simpler and less coupling to implement this as permission check
        IfTransferType(LOCAL_TRANSFER_TYPE, can_read_files),
        SystemProcess(),
    ]
    # Allow submitting new record
    can_create = can_authenticated

    can_search_revisions = [Administration()]

    #
    # Drafts
    #
    # Allow ability to search drafts
    can_search_drafts = can_authenticated
    # Allow reading metadata of a draft
    can_read_draft = can_preview
    # Allow reading files of a draft
    can_draft_read_files = can_preview + [ResourceAccessToken("read")]
    # Allow updating metadata of a draft
    can_update_draft = can_review
    # Allow uploading, updating and deleting files in drafts
    can_draft_create_files = [
        # review is the same as create_files
        IfTransferType(LOCAL_TRANSFER_TYPE, can_review),
        IfTransferType(MULTIPART_TRANSFER_TYPE, can_review),
        SystemProcess(),
    ]
    can_draft_set_content_files = [
        # review is the same as create_files
        IfTransferType(LOCAL_TRANSFER_TYPE, can_review),
        IfTransferType(MULTIPART_TRANSFER_TYPE, can_review),
        SystemProcess(),
    ]
    can_draft_get_content_files = [
        # preview is same as read_files
        IfTransferType(LOCAL_TRANSFER_TYPE, can_draft_read_files),
        SystemProcess(),
    ]
    can_draft_commit_files = [
        # review is the same as create_files
        IfTransferType(LOCAL_TRANSFER_TYPE, can_review),
        IfTransferType(MULTIPART_TRANSFER_TYPE, can_review),
        SystemProcess(),
    ]
    can_draft_update_files = can_review
    can_draft_delete_files = can_review

    can_draft_get_file_transfer_metadata = [SystemProcess()]
    can_draft_update_file_transfer_metadata = [SystemProcess()]

    # Allow enabling/disabling files
    can_manage_files = [
        IfConfig(
            "RDM_ALLOW_METADATA_ONLY_RECORDS",
            then_=[IfNewRecord(then_=can_authenticated, else_=can_review)],
            else_=[SystemProcess()],
        ),
    ]
    # Allow managing record access
    can_manage_record_access = [
        IfConfig(
            "RDM_ALLOW_RESTRICTED_RECORDS",
            then_=[IfNewRecord(then_=can_authenticated, else_=can_review)],
            else_=[],
        )
    ]

    #
    # PIDs
    #
    can_pid_create = can_review
    can_pid_register = can_review
    can_pid_update = can_review
    can_pid_discard = can_review
    can_pid_delete = can_review
    can_pid_manage = [SystemProcess()]

    #
    # Actions
    #
    # Allow to put a record in edit mode (create a draft from record)
    can_edit = [IfDeleted(then_=[Disable()], else_=can_curate)]
    # Allow deleting/discarding a draft and all associated files
    can_delete_draft = can_curate
    # Allow creating a new version of an existing published record.
    can_new_version = [
        IfConfig(
            "RDM_ALLOW_EXTERNAL_DOI_VERSIONING",
            then_=can_curate,
            else_=[IfExternalDOIRecord(then_=[SystemProcess()], else_=can_curate)],
        ),
    ]
    # Allow publishing a new record or changes to an existing record.
    can_publish = [
        IfConfig(
            "RDM_COMMUNITY_REQUIRED_TO_PUBLISH",
            then_=[
                IfAtLeastOneCommunity(
                    then_=can_review,
                    else_=[Administration(), SystemProcess()],
                ),
            ],
            else_=can_review,
        )
    ]
    # Allow lifting a record or draft.
    can_lift_embargo = can_manage

    #
    # Record communities
    #
    # Who can add record to a community
    can_add_community = can_manage
    # Who can remove a community from a record
    can_remove_community_ = [
        RecordOwners(),
        CommunityCurators(),
        SystemProcess(),
    ]
    can_remove_community = [
        IfConfig(
            "RDM_COMMUNITY_REQUIRED_TO_PUBLISH",
            then_=[
                IfOneCommunity(
                    then_=[Administration(), SystemProcess()],
                    else_=can_remove_community_,
                ),
            ],
            else_=can_remove_community_,
        ),
    ]
    # Who can remove records from a community
    can_remove_record = [CommunityCurators(), Administration(), SystemProcess()]
    # Who can add records to a community in bulk
    can_bulk_add = [SystemProcess()]

    #
    # Media files - draft
    #
    can_draft_media_create_files = can_review
    can_draft_media_read_files = can_review
    can_draft_media_set_content_files = [
        IfTransferType(LOCAL_TRANSFER_TYPE, can_review),
        SystemProcess(),
    ]
    can_draft_media_get_content_files = [
        # preview is same as read_files
        IfTransferType(LOCAL_TRANSFER_TYPE, can_preview),
        SystemProcess(),
    ]
    can_draft_media_commit_files = [
        # review is the same as create_files
        IfTransferType(LOCAL_TRANSFER_TYPE, can_review),
        SystemProcess(),
    ]
    can_draft_media_update_files = can_review
    can_draft_media_delete_files = can_review

    #
    # Media files - record
    #
    can_media_read_files = [
        IfRestricted("record", then_=can_view, else_=can_all),
        ResourceAccessToken("read"),
    ]
    can_media_get_content_files = [
        # note: even though this is closer to business logic than permissions,
        # it was simpler and less coupling to implement this as permission check
        IfTransferType(LOCAL_TRANSFER_TYPE, can_read),
        SystemProcess(),
    ]
    can_media_create_files = [Disable()]
    can_media_set_content_files = [Disable()]
    can_media_commit_files = [Disable()]
    can_media_update_files = [Disable()]
    can_media_delete_files = [Disable()]

    #
    # Record deletion workflows
    #
    can_delete = [Administration(), SystemProcess()]
    can_delete_files = [SystemProcess()]
    can_purge = [SystemProcess()]

    #
    # Record and user quota
    #

    can_manage_quota = [
        # moderators
        UserManager,
        SystemProcess(),
    ]
    #
    # Disabled actions (these should not be used or changed)
    #
    # - Records/files are updated/deleted via drafts so we don't support
    #   using below actions.
    can_update = [Disable()]
    can_create_files = [Disable()]
    can_set_content_files = [Disable()]
    can_commit_files = [Disable()]
    can_update_files = [Disable()]

    can_get_file_transfer_metadata = [Disable()]
    can_update_file_transfer_metadata = [Disable()]

    # Used to hide the `parent.is_verified` field. It should be set to
    # correct permissions based on which the field will be exposed only to moderators
    can_moderate = [SystemProcess()]


guest_token = IfRequestType(
    GuestAccessRequest, then_=[GuestAccessRequestToken()], else_=[]
)

guest_token_locked = IfRequestType(
    GuestAccessRequest,
    then_=[
        IfConfig(
            "REQUESTS_LOCKING_ENABLED",
            then_=[
                IfLocked(
                    then_=[Disable()],
                    else_=[GuestAccessRequestToken()],
                ),
            ],
            else_=[GuestAccessRequestToken()],
        ),
    ],
    else_=[],
)


class RDMRequestsPermissionPolicy(RequestPermissionPolicy):
    """Permission policy for requets, adapted to the needs for RDM-Records."""

    can_read = RequestPermissionPolicy.can_read + [guest_token]
    can_update = RequestPermissionPolicy.can_update + [guest_token]
    can_action_submit = RequestPermissionPolicy.can_action_submit + [guest_token]
    can_action_cancel = RequestPermissionPolicy.can_action_cancel + [guest_token]
    can_create_comment = RequestPermissionPolicy.can_create_comment + [
        guest_token_locked
    ]
    can_reply_comment = RequestPermissionPolicy.can_reply_comment + [guest_token_locked]
    can_update_comment = RequestPermissionPolicy.can_update_comment + [
        guest_token_locked
    ]
    can_delete_comment = RequestPermissionPolicy.can_delete_comment + [guest_token]

    # manages GuessAccessRequest payload permissions
    can_manage_access_options = [
        IfCreate(
            then_=[SystemProcess()],
            else_=[
                IfRequestType(
                    GuestAccessRequest,
                    then_=[Status(["submitted"], [Receiver()])],
                    else_=SystemProcess(),
                )
            ],
        )
    ]
