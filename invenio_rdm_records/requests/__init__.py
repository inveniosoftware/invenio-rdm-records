# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2025 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Review request types for InvenioRDM."""

from .access import GuestAccessRequest, UserAccessRequest
from .community_inclusion import CommunityInclusion
from .community_submission import CommunitySubmission
from .file_modification import FileModification
from .record_deletion import RecordDeletion

__all__ = (
    "CommunityInclusion",
    "CommunitySubmission",
    "GuestAccessRequest",
    "UserAccessRequest",
    "RecordDeletion",
    "FileModification",
)
