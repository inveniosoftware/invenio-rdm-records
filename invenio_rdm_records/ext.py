# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2021 CERN.
# Copyright (C) 2019-2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

from flask import flash, g, request, session
from flask_babelex import _
from flask_principal import identity_loaded
from invenio_records_resources.resources.files import FileResource
from invenio_records_resources.services import FileService
from invenio_vocabularies.contrib.affiliations import AffiliationsResource, \
    AffiliationsResourceConfig, AffiliationsService, \
    AffiliationsServiceConfig
from invenio_vocabularies.contrib.subjects import SubjectsResource, \
    SubjectsResourceConfig, SubjectsService, SubjectsServiceConfig
from itsdangerous import SignatureExpired

from . import config
from .resources import RDMDraftFilesResourceConfig, \
    RDMParentRecordLinksResource, RDMParentRecordLinksResourceConfig, \
    RDMRecordFilesResourceConfig, RDMRecordResource, RDMRecordResourceConfig
from .searchconfig import SearchConfig
from .secret_links import LinkNeed, SecretLink
from .services import RDMFileDraftServiceConfig, RDMFileRecordServiceConfig, \
    RDMRecordService, RDMRecordServiceConfig, SecretLinkService
from .services.schemas.metadata_extensions import MetadataExtensions


def verify_token():
    """Verify the token and store it in the session if it's valid."""
    token = request.args.get("token", None)
    if token:
        try:
            data = SecretLink.load_token(token)
            if data:
                session["rdm-records-token"] = data

                # the identity is loaded before this handler is executed
                # so if we want the initial request to be authorized,
                # we need to add the LinkNeed here
                if hasattr(g, "identity"):
                    g.identity.provides.add(LinkNeed(data["id"]))

        except SignatureExpired:
            session.pop("rdm-records-token", None)
            flash(_("Your shared link has expired."))


@identity_loaded.connect
def on_identity_loaded(sender, identity):
    """Add the secret link token need to the freshly loaded Identity."""
    token_data = session.get("rdm-records-token")
    if token_data:
        identity.provides.add(LinkNeed(token_data["id"]))


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
        self.init_services(app)
        self.init_resource(app)
        app.before_request(verify_token)
        app.extensions['invenio-rdm-records'] = self

    def init_config(self, app):
        """Initialize configuration."""
        supported_configurations = [
            'FILES_REST_PERMISSION_FACTORY',
            'RECORDS_REFRESOLVER_CLS',
            'RECORDS_REFRESOLVER_STORE',
            'RECORDS_UI_ENDPOINTS',
            'THEME_SITEURL',
        ]
        overriding_configurations = [
            'PREVIEWER_RECORD_FILE_FACTORY',
        ]

        for k in dir(config):
            if k in supported_configurations or k.startswith('RDM_'):
                app.config.setdefault(k, getattr(config, k))
            if k in overriding_configurations and not app.config.get(k):
                app.config[k] = getattr(config, k)

    def service_configs(self, app):
        """Customized service configs."""
        # Overall record permission policy
        permission_policy = app.config.get('RDM_PERMISSION_POLICY')
        doi_registration = app.config['RDM_RECORDS_DOI_DATACITE_ENABLED']

        # Available facets and sort options
        sort_opts = app.config.get('RDM_SORT_OPTIONS')
        facet_opts = app.config.get('RDM_FACETS')

        # Specific configuration for each search endpoint
        search_opts = SearchConfig(
            app.config.get('RDM_SEARCH'),
            sort=sort_opts,
            facets=facet_opts,
        )
        search_drafts_opts = SearchConfig(
            app.config.get('RDM_SEARCH_DRAFTS'),
            sort=sort_opts,
            facets=facet_opts,
        )
        search_versions_opts = SearchConfig(
            app.config.get('RDM_SEARCH_VERSIONING'),
            sort=sort_opts,
            facets=facet_opts,
        )

        class ServiceConfigs:
            record = RDMRecordServiceConfig.customize(
                permission_policy=permission_policy,
                doi_registration=doi_registration,
                search=search_opts,
                search_drafts=search_drafts_opts,
                search_versions=search_versions_opts,
            )
            file = RDMFileRecordServiceConfig.customize(
                permission_policy=permission_policy,
            )
            file_draft = RDMFileDraftServiceConfig.customize(
                permission_policy=permission_policy,
            )
            affiliations = AffiliationsServiceConfig
            subjects = SubjectsServiceConfig

        return ServiceConfigs

    def init_services(self, app):
        """Initialize vocabulary resources."""
        service_configs = self.service_configs(app)

        # Services
        self.records_service = RDMRecordService(
            service_configs.record,
            files_service=FileService(service_configs.file),
            draft_files_service=FileService(service_configs.file_draft),
            secret_links_service=SecretLinkService(service_configs.record)
        )
        self.affiliations_service = AffiliationsService(
            config=service_configs.affiliations,
        )
        self.subjects_service = SubjectsService(
            config=service_configs.subjects
        )

    def init_resource(self, app):
        """Initialize vocabulary resources."""
        self.records_resource = RDMRecordResource(
            RDMRecordResourceConfig,
            self.records_service,
        )

        # Record files resource
        self.record_files_resource = FileResource(
            service=self.records_service.files,
            config=RDMRecordFilesResourceConfig
        )

        # Draft files resource
        self.draft_files_resource = FileResource(
            service=self.records_service.draft_files,
            config=RDMDraftFilesResourceConfig
        )

        # Parent Records
        self.parent_record_links_resource = RDMParentRecordLinksResource(
            service=self.records_service,
            config=RDMParentRecordLinksResourceConfig
        )

        # Vocabularies
        self.affiliations_resource = AffiliationsResource(
            service=self.affiliations_service,
            config=AffiliationsResourceConfig,
        )
        self.subjects_resource = SubjectsResource(
            service=self.subjects_service,
            config=SubjectsResourceConfig,
        )
