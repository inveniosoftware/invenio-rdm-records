# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""High-level API for wokring with RDM records, files, pids and search."""

from .config import RDMFileDraftServiceConfig, RDMFileRecordServiceConfig, \
    RDMRecordServiceConfig
from .permissions import RDMRecordPermissionPolicy
from .services import RDMRecordService

__all__ = (
    "RDMFileDraftServiceConfig",
    "RDMFileRecordServiceConfig",
    "RDMRecordPermissionPolicy",
    "RDMRecordService",
    "RDMRecordServiceConfig",
)
