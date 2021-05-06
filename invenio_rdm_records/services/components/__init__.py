# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.


"""High-level API for working with RDM service components."""

from .access import AccessComponent
from .metadata import MetadataComponent
from .parent import ParentRecordAccessComponent
from .pids import ExternalPIDsComponent
from .relations import RelationsComponent

__all__ = (
    'AccessComponent',
    'ExternalPIDsComponent',
    'MetadataComponent',
    'ParentRecordAccessComponent',
    'RelationsComponent',
)
