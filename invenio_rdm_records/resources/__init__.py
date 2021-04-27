# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM module to create REST APIs."""

from .config import RDMDraftFilesResourceConfig, \
    RDMManagedPIDProviderResourceConfig, RDMParentRecordLinksResourceConfig, \
    RDMRecordFilesResourceConfig, RDMRecordResourceConfig
from .resources import RDMManagedPIDProviderResource, \
    RDMParentRecordLinksResource, RDMRecordResource

__all__ = (
    "RDMDraftFilesResourceConfig",
    "RDMManagedPIDProviderResource",
    "RDMManagedPIDProviderResourceConfig",
    "RDMParentRecordLinksResource",
    "RDMParentRecordLinksResourceConfig",
    "RDMRecordFilesResourceConfig",
    "RDMRecordResource",
    "RDMRecordResourceConfig",
)
