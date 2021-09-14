# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM PIDs Service."""

from datetime import datetime

from flask_babelex import lazy_gettext as _
from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_drafts_resources.services.records import RecordService
from marshmallow import ValidationError

from .errors import ProviderNotSupportedError

class PIDsService(RecordService):
    """RDM PIDs service."""

    # def get_client(self, client_name):
    #     """Get the provider client from config."""
    #     client_class = self.config.pids_providers_clients[client_name]
    #     return client_class(name=client_name)

    # def get_managed_provider(self, providers_dict):
    #     """Get the provider set as system managed."""
    #     for name, attrs in providers_dict.items():
    #         if attrs["system_managed"]:
    #             return name, attrs

    # def get_required_provider(self, providers_dict):
    #     """Get the provider set as required."""
    #     for name, attrs in providers_dict.items():
    #         if attrs["required"]:
    #             return name, attrs

    def get_provider(self, scheme, provider_name=None):
        """Get a provider from config."""
        providers = self.config.pids_providers[scheme]
        if not provider_name:
            provider_name = providers["default"]  # mandatory default
        try:
            provider_config = providers[provider_name]
        except KeyError:
            raise ProviderNotSupportedError(provider_name, scheme)

        provider_cls = provider_config["provider"]
        return provider_cls()

    def create(self, id_, identity, pid_type, pid_provider=None):
        """Create a `NEW` PID for a given record."""
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        # Permissions
        self.require_permission(identity, "pid_create", record=draft)

        provider = self.get_provider(pid_type, pid_provider)
        pid = provider.create(draft)
        draft.pids[pid_type] = {
            "identifier": pid.pid_value,
            "provider": provider.name
        }
        if provider.client:
            draft.pids[pid_type]["client"] = provider.client.name

        draft.commit()

        db.session.commit()
        self.indexer.index(draft)

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
        )

    def resolve(self, id_, identity, pid_type):
        """Resolve PID to a record (not draft)."""
        # get the pid object
        pid = PersistentIdentifier.get(pid_type=pid_type, pid_value=id_)

        # get related record
        record = self.record_cls.get_record(pid.object_uuid)

        # permissions
        self.require_permission(identity, "read", record=record)

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )

    def discard(self, id_, identity, pid_type, pid_provider=None):
        """Discard a PID for a given draft.

        If the status was `NEW` it will be hard deleted. Otherwise,
        it will be soft deleted (`RESERVED`/`REGISTERED`).
        """
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        # Permissions
        self.require_permission(identity, "pid_delete", record=draft)
        provider = self.get_provider(pid_type, pid_provider)
        pid_attr = draft.pids[pid_type]

        try:
            pid = provider.get_by_record(
                draft.id,
                pid_type=pid_type,
                pid_value=pid_attr["identifier"],
            )
        except PIDDoesNotExistError:
            raise ValidationError(
                message=_("No PID found for type {pid_type}")
                .format(pid_type=pid_type),
                field_name=f"pids.{pid_type}",
            )

        provider.delete(pid, draft)
        draft.pids.pop(pid_type)
        draft.commit()

        db.session.commit()
        self.indexer.index(draft)

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
        )

    def invalidate(self, *args, **kwargs):
        """Invalidates a registered PID of a Record.

        This operation can only be perfomed by an admin.
        """
        raise NotImplementedError()
