# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Access system field for RDM Records."""

from .parent import ParentRecordAccess, ParentRecordAccessField
from .record import RecordAccess, RecordAccessField

__all__ = (
    "ParentRecordAccess",
    "ParentRecordAccessField",
    "RecordAccess",
    "RecordAccessField",
)
