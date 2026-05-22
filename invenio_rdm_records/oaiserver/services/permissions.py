# SPDX-FileCopyrightText: 2022 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Permissions for OAI-PMH service."""

from invenio_administration.generators import Administration
from invenio_records_permissions import BasePermissionPolicy
from invenio_records_permissions.generators import SystemProcess


class OAIPMHServerPermissionPolicy(BasePermissionPolicy):
    """OAI-PMH permission policy."""

    can_read = [Administration(), SystemProcess()]
    can_create = [Administration(), SystemProcess()]
    can_delete = [Administration(), SystemProcess()]
    can_update = [Administration(), SystemProcess()]
    can_read_format = [Administration(), SystemProcess()]
