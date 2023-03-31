# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio RDM Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permissions for the statistics endpoint from Invenio-Stats."""

from .permissions import StatsPermissionTranslator, permissions_policy_lookup_factory

__all__ = (
    "StatsPermissionTranslator",
    "permissions_policy_lookup_factory",
)
