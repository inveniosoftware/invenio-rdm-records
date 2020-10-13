# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""High-level API for wokring with RDM records, files, pids and search."""

from .permissions import RDMRecordPermissionPolicy
from .services import BibliographicRecordService, \
    BibliographicRecordServiceConfig, BibliographicUserRecordsService, \
    BibliographicUserRecordsServiceConfig

__all__ = (
    "BibliographicRecordService",
    "BibliographicRecordServiceConfig",
    "BibliographicUserRecordsService",
    "BibliographicUserRecordsServiceConfig",
    "RDMRecordPermissionPolicy",
)
