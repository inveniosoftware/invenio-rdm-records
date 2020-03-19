# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""
from invenio_indexer.signals import before_record_index

from . import config
from .metadata_extensions import MetadataExtensions, add_es_metadata_extensions


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
            app.config['RDM_RECORDS_METADATA_NAMESPACES'],
            app.config['RDM_RECORDS_METADATA_EXTENSIONS']
        )
        before_record_index.dynamic_connect(
            before_record_index_hook, sender=app, weak=False,
            index='records-record-v1.0.0'
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


def before_record_index_hook(
        sender, json=None, record=None, index=None, **kwargs):
    """Hook to transform Deposits before indexing in ES.

    :param sender: The entity sending the signal.
    :param json: The dumped Record dict which will be indexed.
    :param record: The corresponding Record object.
    :param index: The index in which the json will be indexed.
    :param kwargs: Any other parameters.
    """
    # All thee operations mutate the json
    add_es_metadata_extensions(json)  # TODO: Change for prepare
