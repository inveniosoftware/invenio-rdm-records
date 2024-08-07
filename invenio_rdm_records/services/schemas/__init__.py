# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2021-2023 TU Wien.
# Copyright (C) 2021-2023 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM record schemas."""

from .metadata import MetadataSchema
from .parent import RDMParentSchema
from .record import RDMRecordSchema

__all__ = ("RDMParentSchema", "RDMRecordSchema", "MetadataSchema")
