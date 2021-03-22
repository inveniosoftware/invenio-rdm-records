# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

from flask import flash, g, request, session
from flask_babelex import _
from flask_principal import identity_loaded
from invenio_drafts_resources.resources import RecordResource
from invenio_drafts_resources.services.records import RecordService
from invenio_records_resources.resources.files import FileResource
from invenio_vocabularies.contrib.subjects.subjects import subject_record_type
from itsdangerous import SignatureExpired

from . import config
from .resources import RDMDraftFilesResourceConfig, \
    RDMParentRecordLinksResource, RDMRecordFilesResourceConfig, \
    RDMRecordResourceConfig, RDMParentRecordLinksResourceConfig
from .secret_links import LinkNeed, SecretLink
from .services import RDMRecordServiceConfig
from .services.schemas.metadata_extensions import MetadataExtensions


def verify_token():
    """Verify the token and store it in the session if it's valid."""
    token = request.args.get("token", None)
    if token:
        try:
            data = SecretLink.load_token(token)
            if data:
                session["rdm-records-token"] = data

                # NOTE: the identity is loaded before this handler is executed
                #       so if we want the initial request to be authorized,
                #       we need to add the LinkNeed here
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

    def init_vocabularies(self, app):
        """Initialize vocabulary resources."""


    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.metadata_extensions = MetadataExtensions(
            app.config['RDM_RECORDS_METADATA_NAMESPACES'],
            app.config['RDM_RECORDS_METADATA_EXTENSIONS']
        )
        self.init_services(app)
        self.init_resource(app)
        self.init_vocabularies(app)
        app.before_request(verify_token)
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

    def init_services(self, app):
        """Initialize vocabulary resources."""
        # Services
        # TODO: Rename very long configuration names.
        self.records_service = RecordService(
            config=app.config.get(
                "RDM_RECORDS_BIBLIOGRAPHIC_SERVICE_CONFIG",
                RDMRecordServiceConfig),
        )
        self.subjects_service = subject_record_type.service_cls(
            config=subject_record_type.service_config_cls,
        )

    def init_resource(self, app):
        """Initialize vocabulary resources."""
        # TODO: Rename very long configuration names.
        # Record resource
        self.records_resource = RecordResource(
            service=self.records_service,
            config=app.config.get(
                "RDM_RECORDS_BIBLIOGRAPHIC_RECORD_CONFIG",
                RDMRecordResourceConfig),
        )

        # Record files resource
        self.record_files_resource = FileResource(
            service=self.records_service,
            config=app.config.get(
                "RDM_RECORDS_BIBLIOGRAPHIC_RECORD_FILES_CONFIG",
                RDMRecordFilesResourceConfig),
        )

        # Draft files resource
        self.draft_files_resource = FileResource(
            service=self.records_service,
            config=app.config.get(
                "RDM_RECORDS_BIBLIOGRAPHIC_DRAFT_FILES_CONFIG",
                RDMDraftFilesResourceConfig),
        )

        # Parent Records
        self.parent_record_links_resource = RDMParentRecordLinksResource(
            service=self.records_service,
            config=app.config.get(
                "RDM_RECORDS_BIBLIOGRAPHIC_PARENT_RECORD_LINKS_CONFIG",
                RDMParentRecordLinksResourceConfig
            )
        )

        # Vocabularies
        self.subjects_resource = subject_record_type.resource_cls(
            service=self.subjects_service,
            config=subject_record_type.resource_config_cls,
        )
