# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PID Providers module."""

from .base import BaseClient, BasePIDProvider
from .datacite import DataCiteClient, DataCitePIDProvider
from .unmanaged import UnmanagedPIDProvider

__all__ = (
    "BaseClient",
    "BasePIDProvider",
    "DataCiteClient",
    "DataCitePIDProvider",
    "UnmanagedPIDProvider",
)
