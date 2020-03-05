# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

from . import config
from .metadata_extensions import MetadataExtensions


class InvenioRDMRecords(object):
    """Invenio-RDM-Records extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.metadata_extensions = MetadataExtensions(
            app.config['RDM_RECORDS_METADATA_EXTENSIONS']
        )
        app.extensions['invenio-rdm-records'] = self

    def init_config(self, app):
        """Initialize configuration."""
        supported_configurations = [
            'FILES_REST_PERMISSION_FACTORY',
            'PIDSTORE_RECID_FIELD',
            'RECORDS_REST_ENDPOINTS',
            'RECORDS_REST_FACETS',
            'RECORDS_REST_SORT_OPTIONS',
            'RECORDS_REST_DEFAULT_SORT',
            'RECORDS_FILES_REST_ENDPOINTS',
            'RECORDS_PERMISSIONS_RECORD_POLICY'
        ]

        for k in dir(config):
            if k in supported_configurations or k.startswith('RDM_RECORDS_'):
                app.config.setdefault(k, getattr(config, k))
