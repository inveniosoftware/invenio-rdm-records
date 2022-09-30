# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permissions for OAI-PMH service."""
from invenio_administration.generators import Administration
from invenio_records_permissions import BasePermissionPolicy
from invenio_records_permissions.generators import Admin, AnyUser, SystemProcess


class OAIPMHServerPermissionPolicy(BasePermissionPolicy):
    """OAI-PMH permission policy."""

    can_read = [Admin(), Administration(), SystemProcess()]
    can_create = [Admin(), Administration(), SystemProcess()]
    can_delete = [Admin(), Administration(), SystemProcess()]
    can_update = [Admin(), Administration(), SystemProcess()]
    can_read_format = [Admin(), Administration(), SystemProcess()]
