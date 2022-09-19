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
    RDMDraftFilesResourceConfig,
    RDMParentRecordLinksResourceConfig,
    RDMRecordFilesResourceConfig,
    RDMRecordResourceConfig,
)
from .resources import IIIFResource, RDMParentRecordLinksResource, RDMRecordResource

__all__ = (
    "IIIFResource",
    "IIIFResourceConfig",
    "RDMDraftFilesResourceConfig",
    "RDMParentRecordLinksResource",
    "RDMParentRecordLinksResourceConfig",
    "RDMRecordFilesResourceConfig",
    "RDMRecordResource",
    "RDMRecordResourceConfig",
)
