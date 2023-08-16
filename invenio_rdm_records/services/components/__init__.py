# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.


"""High-level API for working with RDM service components."""

from .access import AccessComponent
from .custom_fields import CustomFieldsComponent
from .metadata import MetadataComponent
from .pids import ParentPIDsComponent, PIDsComponent
from .review import ReviewComponent
from .verified import ContentModerationComponent

__all__ = (
    "AccessComponent",
    "CustomFieldsComponent",
    "MetadataComponent",
    "PIDsComponent",
    "ParentPIDsComponent",
    "ReviewComponent",
    "ContentModerationComponent",
)
