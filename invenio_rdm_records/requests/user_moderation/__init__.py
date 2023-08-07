# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""User moderation actions specific to RDM-Records."""

from .actions import on_approve, on_block, on_restore

__all__ = ("on_approve", "on_block", "on_restore")
