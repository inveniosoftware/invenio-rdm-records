# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom Fields sub service for InvenioRDM."""


from .service import CustomFieldsService, CustomFieldsServiceConfig

__all__ = (
    "CustomFieldsService",
    "CustomFieldsServiceConfig"
)
