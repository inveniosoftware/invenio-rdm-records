# SPDX-FileCopyrightText: 2022-2026 CERN.
# SPDX-License-Identifier: MIT

"""RDM service component for custom fields."""

from .metadata import MetadataComponent


class CustomFieldsComponent(MetadataComponent):
    """Service component for custom fields."""

    field = "custom_fields"
    new_version_skip_fields = []
    new_version_generated_fields = {}
