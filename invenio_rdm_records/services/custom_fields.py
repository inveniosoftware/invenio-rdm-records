# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom Fields sub service for InvenioRDM."""

from invenio_records_resources.services.custom_fields import (
    CustomFieldsServiceConfig as Schema,
)


class CustomFieldsServiceConfig(Schema):
    """Configuration for the Custom Fields service."""

    fields_config_var = "RDM_RECORDS_CUSTOM_FIELDS"
