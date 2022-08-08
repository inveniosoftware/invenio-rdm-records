# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM service component for custom fields."""

from .metadata import MetadataComponent


class CustomFieldsComponent(MetadataComponent):
    """Service component for custom fields."""

    field = "custom_fields"
    new_version_skip_fields = []
