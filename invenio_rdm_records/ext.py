# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2024 CERN.
# Copyright (C) 2019-2021 Northwestern University.
# Copyright (C) 2022 Universität Hamburg.
# Copyright (C) 2023-2024 Graz University of Technology.
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

from warnings import warn

from flask import Blueprint
from flask_iiif import IIIF
from flask_principal import identity_loaded
from invenio_records_resources.resources.files import FileResource

from . import config
from .collections.service import CollectionsService
from .oaiserver.resources.config import OAIPMHServerResourceConfig
from .oaiserver.resources.resources import OAIPMHServerResource
from .oaiserver.services.config import OAIPMHServerServiceConfig
from .oaiserver.services.services import OAIPMHServerService
from .resources import (
    IIIFResource,
    IIIFResourceConfig,
    RDMCommunityRecordsResource,
    RDMCommunityRecordsResourceConfig,
    RDMDraftFilesResourceConfig,
    RDMGrantGroupAccessResourceConfig,
    RDMGrantsAccessResource,
    RDMGrantUserAccessResourceConfig,
    RDMParentGrantsResource,
    RDMParentGrantsResourceConfig,
    RDMParentRecordLinksResource,
    RDMParentRecordLinksResourceConfig,
    RDMRecordCommunitiesResourceConfig,
    RDMRecordFilesResourceConfig,
    RDMRecordRequestsResourceConfig,
    RDMRecordResource,
    RDMRecordResourceConfig,
)
from .resources.config import (
    RDMDraftMediaFilesResourceConfig,
    RDMRecordMediaFilesResourceConfig,
)
from .resources.resources import RDMRecordCommunitiesResource, RDMRecordRequestsResource
from .services import (
    CommunityRecordsService,
    IIIFService,
    RDMCommunityRecordsConfig,
    RDMFileDraftServiceConfig,
    RDMFileRecordServiceConfig,
    RDMRecordCommunitiesConfig,
    RDMRecordRequestsConfig,
    RDMRecordService,
    RDMRecordServiceConfig,
    RecordAccessService,
    RecordRequestsService,
)
from .services.communities.service import RecordCommunitiesService
from .services.community_inclusion.service import CommunityInclusionService
from .services.config import (
    RDMMediaFileDraftServiceConfig,
    RDMMediaFileRecordServiceConfig,
    RDMRecordMediaFilesServiceConfig,
)
from .services.files import RDMFileService
from .services.pids import PIDManager, PIDsService
from .services.review.service import ReviewService
from .utils import verify_token


@identity_loaded.connect
def on_identity_loaded(_, identity):
    """Add secret link token or resource access token need to the freshly loaded Identity."""
    verify_token(identity)


blueprint = Blueprint(
    "invenio_rdm_records",
    __name__,
    template_folder="templates",
    static_folder="static",
)


class InvenioRDMRecords(object):
    """Invenio-RDM-Records extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.init_services(app)
        self.init_resource(app)
        app.extensions["invenio-rdm-records"] = self
        app.register_blueprint(blueprint)
        # Load flask IIIF
        IIIF(app)

    def init_config(self, app):
        """Initialize configuration."""
        supported_configurations = [
            "FILES_REST_PERMISSION_FACTORY",
            "RECORDS_REFRESOLVER_CLS",
            "RECORDS_REFRESOLVER_STORE",
            "RECORDS_UI_ENDPOINTS",
            "THEME_SITEURL",
        ]

        for k in dir(config):
            if (
                k in supported_configurations
                or k.startswith("RDM_")
                or k.startswith("DATACITE_")
                # TODO: This can likely be moved to a separate module
                or k.startswith("IIIF_TILES_")
            ):
                app.config.setdefault(k, getattr(config, k))

        # set default communities namespaces to the global RDM_NAMESPACES
        if not app.config.get("COMMUNITIES_NAMESPACES"):
            app.config["COMMUNITIES_NAMESPACES"] = app.config["RDM_NAMESPACES"]

        if not app.config.get("RDM_FILES_DEFAULT_QUOTA_SIZE"):
            warn(
                "The configuration value 'RDM_FILES_DEFAULT_QUOTA_SIZE' is not set. In future, please set it "
                "explicitly to define your quota size, or be aware that the default value used i.e. FILES_REST_DEFAULT_QUOTA_SIZE will be 10 * (10**9) (10 GB).",
                DeprecationWarning,
            )
        if not app.config.get("RDM_FILES_DEFAULT_MAX_FILE_SIZE"):
            warn(
                "The configuration value 'RDM_FILES_DEFAULT_MAX_FILE_SIZE' is not set. In future, please set it "
                "explicitly to define your max file size, or be aware that the default value used i.e. FILES_REST_DEFAULT_MAX_FILE_SIZE will be 10 * (10**9) (10 GB).",
                DeprecationWarning,
            )

        self.fix_datacite_configs(app)

    def service_configs(self, app):
        """Customized service configs."""

        class ServiceConfigs:
            record = RDMRecordServiceConfig.build(app)
            record_with_media_files = RDMRecordMediaFilesServiceConfig.build(app)
            file = RDMFileRecordServiceConfig.build(app)
            file_draft = RDMFileDraftServiceConfig.build(app)
            media_file = RDMMediaFileRecordServiceConfig.build(app)
            media_file_draft = RDMMediaFileDraftServiceConfig.build(app)
            oaipmh_server = OAIPMHServerServiceConfig
            record_communities = RDMRecordCommunitiesConfig.build(app)
            community_records = RDMCommunityRecordsConfig.build(app)
            record_requests = RDMRecordRequestsConfig.build(app)

        return ServiceConfigs

    def init_services(self, app):
        """Initialize services."""
        service_configs = self.service_configs(app)

        # Services
        self.records_service = RDMRecordService(
            service_configs.record,
            files_service=RDMFileService(service_configs.file),
            draft_files_service=RDMFileService(service_configs.file_draft),
            access_service=RecordAccessService(service_configs.record),
            pids_service=PIDsService(service_configs.record, PIDManager),
            review_service=ReviewService(service_configs.record),
        )

        self.records_media_files_service = RDMRecordService(
            service_configs.record_with_media_files,
            files_service=RDMFileService(service_configs.media_file),
            draft_files_service=RDMFileService(service_configs.media_file_draft),
            pids_service=PIDsService(service_configs.record, PIDManager),
        )

        self.iiif_service = IIIFService(
            records_service=self.records_service, config=None
        )

        self.record_communities_service = RecordCommunitiesService(
            config=service_configs.record_communities,
        )

        self.community_records_service = CommunityRecordsService(
            config=service_configs.community_records,
        )

        self.community_inclusion_service = CommunityInclusionService()
        self.record_requests_service = RecordRequestsService(
            config=service_configs.record_requests
        )

        self.oaipmh_server_service = OAIPMHServerService(
            config=service_configs.oaipmh_server,
        )

        self.collections_service = CollectionsService()

    def init_resource(self, app):
        """Initialize resources."""
        self.records_resource = RDMRecordResource(
            service=self.records_service,
            config=RDMRecordResourceConfig.build(app),
        )

        # Record files resource
        self.record_files_resource = FileResource(
            service=self.records_service.files,
            config=RDMRecordFilesResourceConfig.build(app),
        )

        # Draft files resource
        self.draft_files_resource = FileResource(
            service=self.records_service.draft_files,
            config=RDMDraftFilesResourceConfig.build(app),
        )

        self.record_media_files_resource = FileResource(
            service=self.records_media_files_service.files,
            config=RDMRecordMediaFilesResourceConfig.build(app),
        )

        # Draft files resource
        self.draft_media_files_resource = FileResource(
            service=self.records_media_files_service.draft_files,
            config=RDMDraftMediaFilesResourceConfig.build(app),
        )

        # Parent Records
        self.parent_record_links_resource = RDMParentRecordLinksResource(
            service=self.records_service,
            config=RDMParentRecordLinksResourceConfig.build(app),
        )

        self.parent_grants_resource = RDMParentGrantsResource(
            service=self.records_service,
            config=RDMParentGrantsResourceConfig.build(app),
        )

        self.grant_user_access_resource = RDMGrantsAccessResource(
            service=self.records_service,
            config=RDMGrantUserAccessResourceConfig.build(app),
        )

        self.grant_group_access_resource = RDMGrantsAccessResource(
            service=self.records_service,
            config=RDMGrantGroupAccessResourceConfig.build(app),
        )

        # Record's communities
        self.record_communities_resource = RDMRecordCommunitiesResource(
            service=self.record_communities_service,
            config=RDMRecordCommunitiesResourceConfig.build(app),
        )

        self.record_requests_resource = RDMRecordRequestsResource(
            service=self.record_requests_service,
            config=RDMRecordRequestsResourceConfig.build(app),
        )

        # Community's records
        self.community_records_resource = RDMCommunityRecordsResource(
            service=self.community_records_service,
            config=RDMCommunityRecordsResourceConfig.build(app),
        )

        # OAI-PMH
        self.oaipmh_server_resource = OAIPMHServerResource(
            service=self.oaipmh_server_service,
            config=OAIPMHServerResourceConfig.build(app),
        )

        # IIIF
        self.iiif_resource = IIIFResource(
            service=self.iiif_service,
            config=IIIFResourceConfig.build(app),
        )

    def fix_datacite_configs(self, app):
        """Make sure that the DataCite config items are strings."""
        datacite_config_items = [
            "DATACITE_USERNAME",
            "DATACITE_PASSWORD",
            "DATACITE_FORMAT",
            "DATACITE_PREFIX",
        ]
        for config_item in datacite_config_items:
            if config_item in app.config:
                app.config[config_item] = str(app.config[config_item])


def finalize_app(app):
    """Finalize app.

    NOTE: replace former @record_once decorator
    """
    init(app)


def api_finalize_app(app):
    """Finalize app for api.

    NOTE: replace former @record_once decorator
    """
    init(app)


def init(app):
    """Init app."""
    # Register services - cannot be done in extension because
    # Invenio-Records-Resources might not have been initialized.
    sregistry = app.extensions["invenio-records-resources"].registry
    ext = app.extensions["invenio-rdm-records"]
    sregistry.register(ext.records_service, service_id="records")
    sregistry.register(ext.records_service.files, service_id="files")
    sregistry.register(ext.records_service.draft_files, service_id="draft-files")
    sregistry.register(ext.records_media_files_service, service_id="record-media-files")
    sregistry.register(ext.records_media_files_service.files, service_id="media-files")
    sregistry.register(
        ext.records_media_files_service.draft_files, service_id="draft-media-files"
    )
    sregistry.register(ext.oaipmh_server_service, service_id="oaipmh-server")
    sregistry.register(ext.iiif_service, service_id="rdm-iiif")
    # Register indexers
    iregistry = app.extensions["invenio-indexer"].registry
    iregistry.register(ext.records_service.indexer, indexer_id="records")
    iregistry.register(ext.records_service.draft_indexer, indexer_id="records-drafts")
