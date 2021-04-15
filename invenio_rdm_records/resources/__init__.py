# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM module to create REST APIs."""

from .config import RDMDraftFilesResourceConfig, \
    RDMParentRecordLinksResourceConfig, RDMPIDProviderResourceConfig, \
    RDMRecordFilesResourceConfig, RDMRecordResourceConfig
from .resources import RDMParentRecordLinksResource, RDMPIDProviderResource, \
    RDMRecordResource

__all__ = (
    "RDMDraftFilesResourceConfig",
    "RDMParentRecordLinksResource",
    "RDMRecordResource",
    "RDMParentRecordLinksResourceConfig",
    "RDMPIDProviderResource",
    "RDMPIDProviderResourceConfig",
    "RDMRecordFilesResourceConfig",
    "RDMRecordResourceConfig",
)
