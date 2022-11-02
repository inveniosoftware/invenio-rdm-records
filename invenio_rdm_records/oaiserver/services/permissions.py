# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
# Copyright (C) 2022-2024 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permissions for OAI-PMH service."""
from invenio_administration.generators import Administration
from invenio_records_permissions import BasePermissionPolicy
from invenio_records_permissions.generators import DisableIfReadOnly, SystemProcess


class OAIPMHServerPermissionPolicy(BasePermissionPolicy):
    """OAI-PMH permission policy."""

    can_read = [Administration(), SystemProcess()]
    can_create = [Administration(), SystemProcess(), DisableIfReadOnly()]
    can_delete = [Administration(), SystemProcess(), DisableIfReadOnly()]
    can_update = [Administration(), SystemProcess(), DisableIfReadOnly()]
    can_read_format = [Administration(), SystemProcess()]
