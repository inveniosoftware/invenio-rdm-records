# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2022 Universität Hamburg.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM module to create REST APIs."""

from .config import (
    IIIFResourceConfig,
    RDMCommunityRecordsResourceConfig,
    RDMDraftFilesResourceConfig,
    RDMParentGrantsResourceConfig,
    RDMParentRecordLinksResourceConfig,
    RDMRecordCommunitiesResourceConfig,
    RDMRecordFilesResourceConfig,
    RDMRecordRequestsResourceConfig,
    RDMRecordResourceConfig,
)
from .resources import (
    IIIFResource,
    RDMCommunityRecordsResource,
    RDMParentGrantsResource,
    RDMParentRecordLinksResource,
    RDMRecordRequestsResource,
    RDMRecordResource,
)

__all__ = (
    "IIIFResource",
    "IIIFResourceConfig",
    "RDMCommunityRecordsResource",
    "RDMCommunityRecordsResourceConfig",
    "RDMDraftFilesResourceConfig",
    "RDMParentGrantsResource",
    "RDMParentGrantsResourceConfig",
    "RDMParentRecordLinksResource",
    "RDMParentRecordLinksResourceConfig",
    "RDMRecordCommunitiesResourceConfig",
    "RDMRecordFilesResourceConfig",
    "RDMRecordRequestsResource",
    "RDMRecordRequestsResourceConfig",
    "RDMRecordResource",
    "RDMRecordResourceConfig",
)
