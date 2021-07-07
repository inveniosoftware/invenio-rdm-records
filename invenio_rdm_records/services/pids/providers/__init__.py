# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PID Providers module."""

from .base import BaseClient, BasePIDProvider
from .datacite import DOIDataCiteClient, DOIDataCitePIDProvider
from .oai import OAIPIDClient, OAIPIDProvider
from .unmanaged import UnmanagedPIDProvider

__all__ = (
    "BaseClient",
    "BasePIDProvider",
    "DOIDataCiteClient",
    "DOIDataCitePIDProvider",
    "OAIPIDClient",
    "OAIPIDProvider",
    "UnmanagedPIDProvider",
)
