# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Graz University of Technology.
# Copyright (C) 2022 PNNL.
# Copyright (C) 2021 BNL.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PID Providers module."""

from .base import PIDProvider
from .datacite import DataCiteClient, DataCitePIDProvider
from .osti import OSTIClient, OSTIPIDProvider
from .external import BlockedPrefixes, ExternalPIDProvider
from .oai import OAIPIDProvider

__all__ = (
    "BlockedPrefixes",
    "DataCiteClient",
    "DataCitePIDProvider",
    "OSTIClient",
    "OSTIPIDProvider",
    "ExternalPIDProvider",
    "OAIPIDProvider",
    "PIDProvider",
)
