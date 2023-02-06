# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2022 Universität Hamburg.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""High-level API for wokring with RDM records, files, pids and search."""

from .config import (
    RDMFileDraftServiceConfig,
    RDMFileRecordServiceConfig,
    RDMRecordServiceConfig,
)
from .iiif import IIIFService
from .permissions import RDMRecordPermissionPolicy
from .secret_links import SecretLinkService
from .services import RDMRecordService

__all__ = (
    "IIIFService",
    "RDMFileDraftServiceConfig",
    "RDMFileRecordServiceConfig",
    "RDMRecordPermissionPolicy",
    "RDMRecordService",
    "RDMRecordServiceConfig",
    "SecretLinkService",
)
