# SPDX-FileCopyrightText: 2021 TU Wien.
# SPDX-License-Identifier: MIT

"""RDM record schemas."""

from invenio_drafts_resources.services.records.schema import (
    VersionsSchema as VersionsSchemaBase,
)
from marshmallow_utils.permissions import FieldPermissionsMixin


class VersionsSchema(VersionsSchemaBase, FieldPermissionsMixin):
    """Version schema with field-level permissions."""

    # the field is defined in the superclass
    field_dump_permissions = {
        "is_latest_draft": "edit",
    }
