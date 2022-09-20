# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2022 CERN.
# Copyright (C) 2019-2021 Northwestern University.
# Copyright (C) 2022 Universität Hamburg.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

import warnings

from flask import flash, g, request, session
from flask_babelex import _
from flask_iiif import IIIF
from flask_principal import identity_loaded
from invenio_records_resources.resources.files import FileResource
from invenio_records_resources.services import FileService
from itsdangerous import SignatureExpired

from invenio_rdm_records.oaiserver.resources.config import OAIPMHServerResourceConfig
from invenio_rdm_records.oaiserver.resources.resources import OAIPMHServerResource
from invenio_rdm_records.oaiserver.services.config import OAIPMHServerServiceConfig
from invenio_rdm_records.oaiserver.services.services import OAIPMHServerService

from . import config
from .resources import (
    IIIFResource,
    IIIFResourceConfig,
    RDMDraftFilesResourceConfig,
    RDMParentRecordLinksResource,
    RDMParentRecordLinksResourceConfig,
    RDMRecordFilesResourceConfig,
    RDMRecordResource,
    RDMRecordResourceConfig,
)
from .secret_links import LinkNeed, SecretLink
from .services import (
    IIIFService,
    RDMFileDraftServiceConfig,
    RDMFileRecordServiceConfig,
    RDMRecordService,
    RDMRecordServiceConfig,
    SecretLinkService,
)
from .services.pids import PIDManager, PIDsService
from .services.review.service import ReviewService


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


from flask import Blueprint

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
        app.before_request(verify_token)
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
            ):
                app.config.setdefault(k, getattr(config, k))

        # set default communities namespaces to the global RDM_NAMESPACES
        if not app.config.get("COMMUNITIES_NAMESPACES"):
            app.config["COMMUNITIES_NAMESPACES"] = app.config["RDM_NAMESPACES"]

        # Deprecations
        # Remove when v6.0 LTS is no longer supported.
        deprecated = [
            ("RDM_RECORDS_DOI_DATACITE_ENABLED", "DATACITE_ENABLED"),
            ("RDM_RECORDS_DOI_DATACITE_USERNAME", "DATACITE_USERNAME"),
            ("RDM_RECORDS_DOI_DATACITE_PASSWORD", "DATACITE_PASSWORD"),
            ("RDM_RECORDS_DOI_DATACITE_PREFIX", "DATACITE_PREFIX"),
            ("RDM_RECORDS_DOI_DATACITE_TEST_MODE", "DATACITE_TEST_MODE"),
            ("RDM_RECORDS_DOI_DATACITE_FORMAT", "DATACITE_FORMAT"),
        ]
        for old, new in deprecated:
            if new not in app.config:
                if old in app.config:
                    app.config[new] = app.config[old]
                    warnings.warn(
                        f"{old} has been replaced with {new}. "
                        "Please update your config.",
                        DeprecationWarning,
                    )
            else:
                if old in app.config:
                    warnings.warn(
                        f"{old} is deprecated. Please remove it from your "
                        "config as {new} is already set.",
                        DeprecationWarning,
                    )

        self.fix_datacite_configs(app)

    def service_configs(self, app):
        """Customized service configs."""

        class ServiceConfigs:
            record = RDMRecordServiceConfig.build(app)
            file = RDMFileRecordServiceConfig.build(app)
            file_draft = RDMFileDraftServiceConfig.build(app)
            oaipmh_server = OAIPMHServerServiceConfig

        return ServiceConfigs

    def init_services(self, app):
        """Initialize services."""
        service_configs = self.service_configs(app)

        # Services
        self.records_service = RDMRecordService(
            service_configs.record,
            files_service=FileService(service_configs.file),
            draft_files_service=FileService(service_configs.file_draft),
            secret_links_service=SecretLinkService(service_configs.record),
            pids_service=PIDsService(service_configs.record, PIDManager),
            review_service=ReviewService(service_configs.record),
        )
        self.iiif_service = IIIFService(
            records_service=self.records_service, config=None
        )

        self.oaipmh_server_service = OAIPMHServerService(
            config=service_configs.oaipmh_server,
        )

    def init_resource(self, app):
        """Initialize resources."""
        self.records_resource = RDMRecordResource(
            RDMRecordResourceConfig,
            self.records_service,
        )

        # Record files resource
        self.record_files_resource = FileResource(
            service=self.records_service.files, config=RDMRecordFilesResourceConfig
        )

        # Draft files resource
        self.draft_files_resource = FileResource(
            service=self.records_service.draft_files, config=RDMDraftFilesResourceConfig
        )

        # Parent Records
        self.parent_record_links_resource = RDMParentRecordLinksResource(
            service=self.records_service, config=RDMParentRecordLinksResourceConfig
        )

        # OAI-PMH
        self.oaipmh_server_resource = OAIPMHServerResource(
            service=self.oaipmh_server_service,
            config=OAIPMHServerResourceConfig,
        )

        # IIIF
        self.iiif_resource = IIIFResource(
            service=self.iiif_service,
            config=IIIFResourceConfig,
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
