# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom Fields sub service for InvenioRDM."""

# TODO: This should be a subservice of the main service.
# to be able to access record_cls without hardcoding it.
# - Should the `custom_fields` root package be inside the service?
# - What about the registry?

from .service import CustomFieldsService

__all__ = (
    "CustomFieldsService",
)
