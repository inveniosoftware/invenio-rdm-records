# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""
from celery import shared_task
from invenio_db import db
from invenio_files_rest.signals import file_deleted, file_uploaded
from invenio_indexer.signals import before_record_index
from invenio_vocabularies.contrib.subjects.subjects import subject_record_type

from . import config
from .resources import BibliographicDraftActionResource, \
    BibliographicDraftFilesActionResource, BibliographicDraftFilesResource, \
    BibliographicDraftResource, BibliographicRecordFilesActionResource, \
    BibliographicRecordFilesResource, BibliographicRecordResource, \
    BibliographicUserRecordsResource
from .services import BibliographicDraftFilesService, \
    BibliographicRecordFilesService, BibliographicRecordService, \
    BibliographicUserRecordsService
from .services.schemas.metadata_extensions import MetadataExtensions, \
    add_es_metadata_extensions


class InvenioRDMRecords(object):
    """Invenio-RDM-Records extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_vocabularies(self, app):
        """Initialize vocabulary resources."""
        self.subjects_service = subject_record_type.service_cls(
            config=subject_record_type.service_config_cls,
        )
        self.subjects_resource = subject_record_type.resource_cls(
            service=self.subjects_service,
            config=subject_record_type.resource_config_cls,
        )

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.metadata_extensions = MetadataExtensions(
            app.config['RDM_RECORDS_METADATA_NAMESPACES'],
            app.config['RDM_RECORDS_METADATA_EXTENSIONS']
        )
        self.init_resource(app)
        self.init_vocabularies(app)
        app.extensions['invenio-rdm-records'] = self

    def init_config(self, app):
        """Initialize configuration."""
        supported_configurations = [
            'FILES_REST_PERMISSION_FACTORY',
            'RECORDS_UI_ENDPOINTS',
            'THEME_SITEURL',
        ]
        overriding_configurations = [
            'PREVIEWER_RECORD_FILE_FACTORY',
        ]

        for k in dir(config):
            if k in supported_configurations or k.startswith('RDM_RECORDS_'):
                app.config.setdefault(k, getattr(config, k))
            if k in overriding_configurations and not app.config.get(k):
                app.config[k] = getattr(config, k)

    def init_resource(self, app):
        """Initialize vocabulary resources."""
        # Records
        self.records_service = BibliographicRecordService(
            config=app.config.get("RDM_RECORDS_RECORDS_SERVICE_CONFIG"),
        )

        self.records_resource = BibliographicRecordResource(
            service=self.records_service,
            config=app.config.get("RDM_RECORDS_RECORDS_RESOURCE_CONFIG"),
        )

        # Drafts
        self.drafts_resource = BibliographicDraftResource(
            service=self.records_service,
            config=app.config.get("RDM_RECORDS_DRAFTS_RESOURCE_CONFIG"),
        )

        self.drafts_action_resource = BibliographicDraftActionResource(
            service=self.records_service,
            config=app.config.get(
                "RDM_RECORDS_DRAFTS_ACTION_RESOURCE_CONFIG"),
        )

        # User
        self.user_records_service = BibliographicUserRecordsService(
            config=app.config.get("RDM_RECORDS_USER_RECORDS_SERVICE_CONFIG"),
        )

        self.user_records_resource = BibliographicUserRecordsResource(
            service=self.user_records_service,
            config=app.config.get("RDM_RECORDS_USER_RECORDS_RESOURCE_CONFIG"),
        )

        # Files
        self.record_files_service = BibliographicRecordFilesService(
            config=app.config.get("RDM_RECORDS_RECORD_FILES_SERVICE_CONFIG"),
        )

        self.record_files_resource = BibliographicRecordFilesResource(
            service=self.record_files_service,
            config=app.config.get("RDM_RECORDS_RECORD_FILES_RESOURCE_CONFIG"),
        )

        self.record_files_action_resource = \
            BibliographicRecordFilesActionResource(
                service=self.record_files_service,
                config=app.config.get(
                    "RDM_RECORDS_RECORD_FILES_ACTION_RESOURCE_CONFIG"),
            )

        self.draft_files_service = BibliographicDraftFilesService(
            config=app.config.get("RDM_RECORDS_DRAFT_FILES_SERVICE_CONFIG"),
        )

        self.draft_files_resource = BibliographicDraftFilesResource(
            service=self.draft_files_service,
            config=app.config.get("RDM_RECORDS_DRAFT_FILES_RESOURCE_CONFIG"),
        )

        self.draft_files_action_resource = \
            BibliographicDraftFilesActionResource(
                service=self.draft_files_service,
                config=app.config.get(
                    "RDM_RECORDS_DRAFT_FILES_ACTION_RESOURCE_CONFIG"),
            )
