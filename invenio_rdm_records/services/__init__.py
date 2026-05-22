# SPDX-FileCopyrightText: 2023-2024 CERN.
# SPDX-FileCopyrightText: 2022 Universität Hamburg.
# SPDX-License-Identifier: MIT

"""High-level API for wokring with RDM records, files, pids and search."""

from .access import RecordAccessService
from .community_records import CommunityRecordsService
from .config import (
    RDMCommunityRecordsConfig,
    RDMFileDraftServiceConfig,
    RDMFileRecordServiceConfig,
    RDMRecordCommunitiesConfig,
    RDMRecordMediaFilesServiceConfig,
    RDMRecordRequestsConfig,
    RDMRecordServiceConfig,
)
from .iiif import IIIFService
from .permissions import RDMRecordPermissionPolicy
from .requests import RecordRequestsService
from .services import RDMRecordService

__all__ = (
    "IIIFService",
    "RDMFileDraftServiceConfig",
    "RDMFileRecordServiceConfig",
    "RDMRecordPermissionPolicy",
    "RDMRecordService",
    "RDMRecordServiceConfig",
    "RecordAccessService",
    "RDMRecordCommunitiesConfig",
    "RDMCommunityRecordsConfig",
    "CommunityRecordsService",
    "RDMRecordRequestsConfig",
    "RecordRequestsService",
    "RDMRecordMediaFilesServiceConfig",
)
