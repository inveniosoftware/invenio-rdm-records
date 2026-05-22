# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-FileCopyrightText: 2021 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""PID Providers module."""

from .base import PIDProvider
from .crossref import CrossrefClient, CrossrefPIDProvider
from .datacite import DataCiteClient, DataCitePIDProvider
from .external import BlockedPrefixes, ExternalPIDProvider
from .oai import OAIPIDProvider

__all__ = (
    "BlockedPrefixes",
    "CrossrefClient",
    "CrossrefPIDProvider",
    "DataCiteClient",
    "DataCitePIDProvider",
    "ExternalPIDProvider",
    "OAIPIDProvider",
    "PIDProvider",
)
