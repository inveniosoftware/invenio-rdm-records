# SPDX-FileCopyrightText: 2023 TU Wien.
# SPDX-License-Identifier: MIT

"""Permissions for the statistics endpoint from Invenio-Stats."""

from .permissions import StatsPermissionTranslator, permissions_policy_lookup_factory

__all__ = (
    "StatsPermissionTranslator",
    "permissions_policy_lookup_factory",
)
