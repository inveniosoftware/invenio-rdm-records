# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utils for Invenio RDM Records."""

from flask import current_app


def is_doi_locally_managed(doi_value):
    """Determine if a DOI value is locally managed."""
    return any(doi_value.startswith(prefix) for prefix in
               current_app.config['RDM_RECORDS_LOCAL_DOI_PREFIXES'])
