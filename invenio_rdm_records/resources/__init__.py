# SPDX-FileCopyrightText: 2020-2024 CERN.
# SPDX-FileCopyrightText: 2022 Universität Hamburg.
# SPDX-License-Identifier: MIT

"""Invenio RDM module to create REST APIs."""

from .config import (
    RDMCollectionsResourceConfig,
    RDMCommunityRecordsResourceConfig,
    RDMDraftFilesResourceConfig,
    RDMGrantGroupAccessResourceConfig,
    RDMGrantUserAccessResourceConfig,
    RDMParentGrantsResourceConfig,
    RDMParentRecordLinksResourceConfig,
    RDMRecordCommunitiesResourceConfig,
    RDMRecordFilesResourceConfig,
    RDMRecordRequestsResourceConfig,
    RDMRecordResourceConfig,
)
from .iiif import IIIFResource, IIIFResourceConfig
from .resources import (
    RDMCommunityRecordsResource,
    RDMGrantsAccessResource,
    RDMParentGrantsResource,
    RDMParentRecordLinksResource,
    RDMRecordRequestsResource,
    RDMRecordResource,
)

__all__ = (
    "IIIFResource",
    "RDMCollectionsResourceConfig",
    "IIIFResourceConfig",
    "RDMCommunityRecordsResource",
    "RDMCommunityRecordsResourceConfig",
    "RDMDraftFilesResourceConfig",
    "RDMParentGrantsResource",
    "RDMGrantsAccessResource",
    "RDMParentGrantsResourceConfig",
    "RDMGrantUserAccessResourceConfig",
    "RDMGrantGroupAccessResourceConfig",
    "RDMParentRecordLinksResource",
    "RDMParentRecordLinksResourceConfig",
    "RDMRecordCommunitiesResourceConfig",
    "RDMRecordFilesResourceConfig",
    "RDMRecordRequestsResource",
    "RDMRecordRequestsResourceConfig",
    "RDMRecordResource",
    "RDMRecordResourceConfig",
)
