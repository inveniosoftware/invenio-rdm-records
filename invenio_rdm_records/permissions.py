# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Permissions for Invenio RDM Records."""

from invenio_drafts_resources.services.records.permissions import \
    RecordDraftPermissionPolicy
from invenio_records_permissions.generators import AnyUser


class RDMRecordPermissionPolicy(RecordDraftPermissionPolicy):
    """Access control configuration for records.

    Note that even if the array is empty, the invenio_access Permission class
    always adds the ``superuser-access``, so admins will always be allowed.

    - Create action given to everyone for now.
    - Read access given to everyone if public record and given to owners
      always. (inherited)
    - Update access given to record owners. (inherited)
    - Delete access given to admins only. (inherited)
    """

    # TODO: Change all below when permissions settled
    can_create = [AnyUser()]
    can_update_files = [AnyUser()]
    can_publish = [AnyUser()]
    can_read = [AnyUser()]
