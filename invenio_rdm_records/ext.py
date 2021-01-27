# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

from invenio_vocabularies.contrib.subjects.subjects import subject_record_type

from . import config
from .resources import RDMDraftActionResource, RDMDraftFilesActionResource, \
    RDMDraftFilesResource, RDMDraftResource, RDMRecordFilesActionResource, \
    RDMRecordFilesResource, RDMRecordResource, RDMUserRecordsResource
from .services import RDMDraftFilesService, RDMRecordFilesService, \
    RDMRecordService, RDMUserRecordsService
from .services.schemas.metadata_extensions import MetadataExtensions


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
        self.records_service = RDMRecordService(
            config=app.config.get(RDMRecordService.config_name),
        )

        self.records_resource = RDMRecordResource(
            service=self.records_service,
            config=app.config.get(RDMRecordResource.config_name),
        )

        # Drafts
        self.drafts_resource = RDMDraftResource(
            service=self.records_service,
            config=app.config.get(RDMDraftResource.config_name),
        )

        self.drafts_action_resource = RDMDraftActionResource(
            service=self.records_service,
            config=app.config.get(
                RDMDraftActionResource.config_name),
        )

        # User
        self.user_records_service = RDMUserRecordsService(
            config=app.config.get(
                RDMUserRecordsService.config_name),
        )

        self.user_records_resource = RDMUserRecordsResource(
            service=self.user_records_service,
            config=app.config.get(
                RDMUserRecordsResource.config_name),
        )

        # Files
        self.record_files_service = RDMRecordFilesService(
            config=app.config.get(
                RDMRecordFilesService.config_name),
        )

        self.record_files_resource = RDMRecordFilesResource(
            service=self.record_files_service,
            config=app.config.get(
                RDMRecordFilesResource.config_name),
        )

        self.record_files_action_resource = \
            RDMRecordFilesActionResource(
                service=self.record_files_service,
                config=app.config.get(
                    RDMRecordFilesActionResource.config_name),
            )

        self.draft_files_service = RDMDraftFilesService(
            config=app.config.get(RDMDraftFilesService.config_name),
        )

        self.draft_files_resource = RDMDraftFilesResource(
            service=self.draft_files_service,
            config=app.config.get(RDMDraftFilesResource.config_name),
        )

        self.draft_files_action_resource = \
            RDMDraftFilesActionResource(
                service=self.draft_files_service,
                config=app.config.get(
                    RDMDraftFilesActionResource.config_name),
            )
