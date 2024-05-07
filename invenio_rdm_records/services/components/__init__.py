# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""High-level API for working with RDM service components."""

from invenio_drafts_resources.services.records.components import (
    DraftFilesComponent,
    DraftMediaFilesComponent,
    PIDComponent,
    RelationsComponent,
)

from .access import AccessComponent
from .custom_fields import CustomFieldsComponent
from .metadata import MetadataComponent
from .pids import ParentPIDsComponent, PIDsComponent
from .record_deletion import RecordDeletionComponent
from .record_files import RecordFilesProcessorComponent
from .review import ReviewComponent
from .verified import ContentModerationComponent

# Default components - order matters!
DefaultRecordsComponents = [
    MetadataComponent,
    CustomFieldsComponent,
    AccessComponent,
    DraftFilesComponent,
    DraftMediaFilesComponent,
    RecordFilesProcessorComponent,
    RecordDeletionComponent,
    # for the internal `pid` field
    PIDComponent,
    # for the `pids` field (external PIDs)
    PIDsComponent,
    ParentPIDsComponent,
    RelationsComponent,
    ReviewComponent,
    ContentModerationComponent,
]


__all__ = (
    "AccessComponent",
    "ContentModerationComponent",
    "CustomFieldsComponent",
    "MetadataComponent",
    "PIDsComponent",
    "ParentPIDsComponent",
    "RecordDeletionComponent",
    "ReviewComponent",
    "DefaultRecordsComponents",
)
