# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2022 Universität Hamburg.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

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
