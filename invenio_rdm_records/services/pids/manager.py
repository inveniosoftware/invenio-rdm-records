# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM PIDs Service."""

from flask.globals import current_app
from flask_babelex import lazy_gettext as _
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PIDStatus
from marshmallow import ValidationError

from .errors import PIDSchemeNotSupportedError, ProviderNotSupportedError


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
            return providers[provider_name]
        except KeyError:
            raise ProviderNotSupportedError(provider_name, scheme)

    def _validate_pids_schemes(self, pids):
        """Validate the pid schemes that are supported by the service.

        This would only fail on the REST API or a misconfigured web UI.
        The marshmallow schema validates that the structure of the data is
        correct. This function validates that the given pids schemes are
        actually supported.
        """
        supported_schemes = set(self._providers.keys())
        input_schemes = set(pids.keys())
        unknown_schemes = input_schemes - supported_schemes
        if unknown_schemes:
            raise PIDSchemeNotSupportedError(unknown_schemes)

    def _validate_pids(self, pids, record, errors):
        """Validate an iterator of PIDs.

        This function assumes all pid schemes are supported by the system.
        """
        for scheme, pid in pids.items():
            provider = self._get_provider(scheme, pid.get("provider"))
            success, val_errors = provider.validate(record=record, **pid)
            if not success:
                errors.append({
                    "field": f"pids.{scheme}",
                    "messages": val_errors
                })

    def _validate_identifiers(self, pids, errors):
        """Validate and normalize identifiers."""
        # TODO: Refactor to get it injected instead.
        conf = current_app.config['RDM_PERSISTENT_IDENTIFIERS']

        identifiers = []
        for scheme, pids_attrs in pids.items():
            identifier = pids_attrs.get('identifier')

            validator = conf.get(scheme, {}).get('validator', lambda x: True)
            normalizer = conf.get(scheme, {}).get('normalizer')
            label = conf.get(scheme, {}).get('label', scheme)

            if identifier:
                if not validator(identifier):
                    errors.append({
                        "field": f"pids.{scheme}",
                        "messages": [_("Invalid {scheme}").format(
                            scheme=label
                        )]
                    })
                else:
                    if normalizer is not None:
                        identifiers.append((scheme, normalizer(identifier)))

        # Modify outside of iteration - updates the pids globally
        for scheme, id_ in identifiers:
            pids[scheme]['identifier'] = id_

    def validate(self, pids, record, errors=None, raise_errors=False):
        """Validate PIDs."""
        errors = [] if errors is None else errors
        self._validate_pids_schemes(pids)
        self._validate_identifiers(pids, errors)
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
                pid = provider.get(identifier)
            except PIDDoesNotExistError:
                pid = None
            # the pid will be reactivated if it was deleted
            if not pid or pid.is_deleted():
                pid = provider.create(
                    record=draft,
                    pid_value=identifier,
                    status=PIDStatus.RESERVED,
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

    def create_all(self, draft, pids=None, schemes=None):
        """Create many PIDs for a draft."""
        result = {}

        # Create with an identifier value provided
        for scheme, pid_attrs in (pids or {}).items():
            result[scheme] = self.create(
                draft,
                scheme,
                pid_attrs["identifier"],
                pid_attrs.get("provider"),
            )

        # Create without an identifier value provided (only the scheme)
        for scheme in (schemes or []):
            result[scheme] = self.create(draft, scheme)

        return result

    def update(self, record, scheme):
        """Update a registered PID on a remote provider."""
        pid_attrs = record.pids.get(scheme, None)
        if not pid_attrs:
            raise ValidationError(
                message=_("PID not found for type {scheme}")
                .format(scheme=scheme),
                field_name=f"pids",
            )

        provider = self._get_provider(scheme, pid_attrs["provider"])
        pid = provider.get(pid_attrs["identifier"])

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
        pid = provider.get(pid_attrs["identifier"])

        provider.register(pid, record=record, url=url)

    def discard(self, scheme, identifier, provider_name=None):
        """Discard a PID."""
        provider = self._get_provider(scheme, provider_name)
        pid = provider.get(identifier)
        if not provider.can_modify(pid):
            raise ValidationError(message=[{
                    "field": f"pids.{scheme}",
                    "message": _(
                        "Cannot discard a reserved or registered persistent "
                        "identifier."
                    )
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
