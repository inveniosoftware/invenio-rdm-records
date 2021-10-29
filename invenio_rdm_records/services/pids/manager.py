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
from invenio_drafts_resources.services.records import RecordService
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from marshmallow import ValidationError

from .errors import PIDSchemeNotSupportedError, ProviderNotSupportedError
from .tasks import register_pid, update_pid


class PIDManager:
    """RDM PIDs Manager."""

    def __init__(self, providers):
        """Constructor for RecordService."""
        self._providers = providers

    def _get_provider(self, scheme, provider_name=None):
        """Get a provider."""
        providers = self._providers[scheme]
        if not provider_name:
            provider_name = providers["default"]  # mandatory default
        try:
            provider_cls = providers[provider_name]
            return provider_cls()
        except KeyError:
            raise ProviderNotSupportedError(provider_name, scheme)

    def _validate_pids_schemes(self, pids):
        """Validate the pid schemes are supported by the service.

        This would only fail on the REST API or a misconfigured web UI.
        The marshmallow schema validates that the structure of the data is
        correct. This function validates that the given pids are actually
        supported.
        """
        provider_schemes = set(self._providers.keys())
        all_schemes = set(pids.keys())
        unknown_schemes = all_schemes - provider_schemes
        if unknown_schemes:
            raise PIDSchemeNotSupportedError(unknown_schemes)

    def _validate_pids(self, pids, record, errors):
        """Validate an iterator of PIDs.

        This function assumes all pid schemes are supported by the system.
        """
        for scheme, pid in pids.items():
            provider_name = pid.get("provider")
            provider = self._get_provider(scheme, provider_name)
            success, val_errors = provider.validate(record=record, **pid)
            if not success:
                errors.append({
                    "field": f"pids.{scheme}",
                    "message": val_errors
                })

    def validate(self, pids, record, errors=None, raise_errors=False):
        """Validate PIDs."""
        errors = [] if errors is None else errors
        self._validate_pids_schemes(pids)
        self._validate_pids(pids, record, errors)

        if raise_errors and errors:
            raise ValidationError(message=errors)

    def read(self, scheme, identifier, provider_name):
        """Read a pid."""
        provider = self._get_provider(scheme, provider_name)

        return provider.get(identifier)

    def create(self, draft, scheme, identifier=None, provider_name=None):
        """Create a pid for a draft.

        If the pid is deleted it re-activates it.
        If the pid exists it does not modify it (idempotent).
        """
        provider = self._get_provider(scheme, provider_name)
        pid_attrs = {}
        if identifier:
            try:
                pid = provider.get(pid_value=identifier)
            except PIDDoesNotExistError:
                pid = None
            # the pid will be reactivated if it was deleted
            if not pid or pid.is_deleted():
                pid = provider.create(
                    record=draft, value=identifier, status=PIDStatus.RESERVED
                )
            pid_attrs = {
                "identifier": identifier,
                "provider": provider.name
            }
        else:
            if draft.pids.get(scheme):
                raise ValidationError(
                    message=_("A PID already exists for type {scheme}")
                    .format(scheme=scheme),
                    field_name=f"pids.{scheme}",
                )
            if not provider.is_managed():
                raise ValidationError(
                    message=_("External identifier value is required."),
                    field_name=f"pids.{scheme}"
                )
            pid = provider.create(draft)
            pid_attrs = {
                "identifier": pid.pid_value,
                "provider": provider.name
            }

        if provider.client:  # provider and identifier already in dict
            pid_attrs["client"] = provider.client.name

        return pid_attrs

    def create_all(self, draft, pids):
        """Create many PIDs for a draft."""
        if isinstance(pids, dict):
            for scheme, pid_attrs in pids.items():
                pids[scheme] = self.create(
                    draft,
                    scheme,
                    pid_attrs["identifier"],
                    pid_attrs.get("provider"),
                )
            return pids

        else:  # list
            _pids = {}
            for scheme in pids:
                _pids[scheme] = self.create(draft, scheme)

            return _pids

    def update_remote(self, record, scheme):
        """Update a registered PID on a remote provider."""
        pid_attrs = record.pids.get(scheme, None)
        if not pid_attrs:
            raise ValidationError(
                message=_("PID not found for type {scheme}")
                .format(scheme=scheme),
                field_name=f"pids",
            )

        provider_name = pid_attrs["provider"]
        provider = self._get_provider(scheme, provider_name)
        pid_value = pid_attrs["identifier"]
        pid = provider.get(pid_value=pid_value, pid_type=scheme)
        provider.update(pid, record=record)

    def reserve(self, draft, scheme, identifier, provider_name):
        """Reserve a PID."""
        provider = self._get_provider(scheme, provider_name)
        pid = provider.get(identifier)
        if pid.is_new():  # not reserved and not registered
            provider.reserve(pid, record=draft)

    def reserve_all(self, draft, pids):
        """Reserve PIDs from a list."""
        for scheme, pid_attrs in pids.items():
            self.reserve(
                draft, scheme, pid_attrs["identifier"], pid_attrs["provider"]
            )

    def register(self, record, scheme, url):
        """Register a PID of a record."""
        pid_attrs = record.pids.get(scheme, None)
        if not pid_attrs:
            raise ValidationError(
                message=_("PID not found for type {scheme}")
                .format(scheme=scheme),
                field_name=f"pids",
            )

        provider = self._get_provider(scheme, pid_attrs["provider"])
        pid_value = pid_attrs["identifier"]
        pid = provider.get(pid_value=pid_value, pid_type=scheme)

        provider.register(
            pid, record=record, url=url
        )

    def discard(self, scheme, identifier, provider_name=None):
        """Discard a PID."""
        provider = self._get_provider(scheme, provider_name)
        pid = provider.get(pid_value=identifier)
        if not provider.can_modify(pid):
            raise ValidationError(message=[{
                    "field": f"pids.{scheme}",
                    "message": _("Cannot modify a reserved or registered PID.")
                }])

        provider.delete(pid)

    def discard_all(self, pids):
        """Discard all PIDs."""
        for scheme, pid_attrs in pids.items():
            try:
                self.discard(
                    scheme,
                    pid_attrs["identifier"],
                    pid_attrs["provider"],
                )
            except PIDDoesNotExistError:
                pass  # might not have been saved to DB yet
