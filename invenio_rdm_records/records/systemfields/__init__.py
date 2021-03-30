# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""System Fields for RDM Records."""

from .access import ParentRecordAccessField, RecordAccessField
from .has_draftcheck import HasDraftCheckField

__all__ = (
    "HasDraftCheckField",
    "ParentRecordAccessField",
    "RecordAccessField",
)
