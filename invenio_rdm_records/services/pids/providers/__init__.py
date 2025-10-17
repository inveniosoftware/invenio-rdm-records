# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

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
