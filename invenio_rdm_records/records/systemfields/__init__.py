# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""System Fields for RDM Records."""

from .access import ParentRecordAccessField, RecordAccessField
from .deletion_status import RecordDeletionStatusField
from .draft_status import DraftStatus
from .has_draftcheck import HasDraftCheckField
from .is_verified import IsVerifiedField
from .statistics import RecordStatisticsField
from .tombstone import TombstoneField

__all__ = (
    "DraftStatus",
    "HasDraftCheckField",
    "IsVerifiedField",
    "ParentRecordAccessField",
    "RecordAccessField",
    "RecordStatisticsField",
    "RecordDeletionStatusField",
    "TombstoneField",
)
