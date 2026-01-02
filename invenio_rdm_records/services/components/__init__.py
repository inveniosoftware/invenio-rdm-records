# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2025 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""High-level API for working with RDM service components."""

from invenio_checks.components import ChecksComponent
from invenio_drafts_resources.services.records.components import (
    DraftMediaFilesComponent,
    PIDComponent,
    RelationsComponent,
)

from .access import AccessComponent
from .custom_fields import CustomFieldsComponent
from .files import RDMDraftFilesComponent
from .internal_notes import InternalNotesComponent
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
    RDMDraftFilesComponent,
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
    InternalNotesComponent,
    ChecksComponent,
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
