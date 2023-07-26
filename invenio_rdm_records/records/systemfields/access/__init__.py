# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Access system field for RDM Records."""

from .access_settings import AccessSettings
from .embargo import Embargo
from .field import (
    ParentRecordAccess,
    ParentRecordAccessField,
    RecordAccess,
    RecordAccessField,
)
from .grants import Grant, Grants
from .links import Link, Links
from .owners import Owner
from .protection import Protection

__all__ = (
    "Embargo",
    "Grant",
    "Grants",
    "Link",
    "Links",
    "Owner",
    "AccessSettings",
    "ParentRecordAccess",
    "ParentRecordAccessField",
    "Protection",
    "RecordAccess",
    "RecordAccessField",
)
