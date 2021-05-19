# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020-2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM Record Service."""

from flask_babelex import lazy_gettext as _
from invenio_db import db
from invenio_drafts_resources.services.records import RecordService
from invenio_pidstore.errors import PIDDoesNotExistError
from marshmallow.exceptions import ValidationError


class RDMRecordService(RecordService):
    """RDM record service."""

    def __init__(self, config, files_service=None, draft_files_service=None,
                 secret_links_service=None, pids_service=None):
        """Constructor for RecordService."""
        super().__init__(config, files_service, draft_files_service)
        self._secret_links = secret_links_service
        self._pids = pids_service

    #
    # Subservice
    #
    @property
    def secret_links(self):
        """Record secret link service."""
        return self._secret_links

    @property
    def pids(self):
        """Record pids service."""
        return self._pids

    def get_client(self, client_name):
        """Get the provider client from config."""
        client_class = self.config.pids_providers_clients[client_name]
        return client_class(name=client_name)

    def get_managed_provider(self, providers_dict):
        """Get the provider set as system managed."""
        for name, attrs in providers_dict.items():
            if attrs["system_managed"]:
                return name, attrs

    def get_required_provider(self, providers_dict):
        """Get the provider set as required."""
        for name, attrs in providers_dict.items():
            if attrs["required"]:
                return name, attrs

    def get_provider(self, scheme, provider_name=None, client_name=None):
        """Get a provider from config."""
        try:
            providers = self.config.pids_providers[scheme]

            if provider_name:
                provider_config = providers[provider_name]
            else:
                # if no name provided, one of the configured must be required
                _provider = self.get_required_provider(providers)
                if not _provider:
                    # there are no required providers
                    return None
                else:
                    name, provider_config = _provider

            provider_class = provider_config["provider"]
        except ValueError:
            raise ValidationError(
                message=_(f"Unknown PID provider for {scheme}"),
                field_name=f"pids.{scheme}",
            )

        try:
            if client_name:
                client = self.get_client(client_name)
                return provider_class(client)
            elif provider_config["system_managed"]:
                # use as default the client configured for the provider
                provider_name = provider_class.name
                client = self.get_client(provider_name)
                return provider_class(client)

            return provider_class()
        except ValueError:
            raise ValidationError(
                message=_(f"{client_name} not supported for PID {scheme}"),
                ield_name=f"pids.{scheme}",
            )
