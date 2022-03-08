# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permissions for OAI-PMH service."""

from invenio_records_permissions import BasePermissionPolicy
from invenio_records_permissions.generators import Admin, AnyUser, \
    SystemProcess


class OAIPMHServerPermissionPolicy(BasePermissionPolicy):
    """OAI-PMH permission policy."""

    can_read = [Admin(), SystemProcess()]
    can_create = [Admin(), SystemProcess()]
    can_delete = [Admin(), SystemProcess()]
    can_update = [Admin(), SystemProcess()]
    can_read_format = [Admin(), SystemProcess()]
