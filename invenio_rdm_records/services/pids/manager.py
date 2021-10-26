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
from invenio_records_resources.services.errors import PermissionDeniedError
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
        pids_providers = set(self._providers.keys())
        all_pids = set(pids.keys())
        unknown_pids = all_pids - pids_providers
        if unknown_pids:
            raise PIDSchemeNotSupportedError(unknown_pids)

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

    def validate(self, identity, pids, record, errors=None):
        """Validate PIDs."""
        errors = [] if errors is None else errors
        self._validate_pids_schemes(pids)
        self._validate_pids(pids, record, errors)

        return pids

    def create(self, draft, pid_attrs, scheme):
        """Create a pid for a draft.

        If the pid is deleted it re-activates it.
        It does not fail if the pid already exists (idempotent).
        """
        pid_value = pid_attrs["identifier"]
        provider = self._get_provider(scheme, pid_attrs.get("provider"))
        # the pid will be reactivated if it was deleted
        try:
            pid = provider.get(pid_value=pid_value)
        except PIDDoesNotExistError:
            pid = None

        if not pid or pid.is_deleted():
            pid = provider.create(
                record=draft, value=pid_value, status=PIDStatus.RESERVED
            )

        if provider.client:  # provider and identifier already in dict
            pid_attrs["client"] = provider.client.name

        return pid_attrs

    def create_by_scheme(self, draft, scheme, pid_provider=None):
        """Creates a pid for a specified scheme."""
        provider = self._get_provider(scheme, pid_provider)
        pid = provider.create(draft)
        pid_attrs = {
            "identifier": pid.pid_value,
            "provider": provider.name
        }
        if provider.client:
            pid_attrs["client"] = provider.client.name

        return pid_attrs

    def create_many(self, draft, pids):
        """Create many PIDs for a draft."""
        for scheme, pid_attrs in pids.items():
            pids[scheme] = self.create(draft, pid_attrs, scheme)

        return pids

    def create_many_by_scheme(self, draft, schemes):
        """Create the required PIDs."""
        pids = {}
        for scheme in schemes:
            if not draft.pids.get(scheme):
                # FIXME: should fail if required and external but no value
                provider = self._get_provider(scheme)
                # FIXME: raising here is too ad hoc
                if not provider.is_managed():
                    raise ValidationError(
                        message=_("External identifier value is required."),
                        field_name=f"pids.{scheme}"
                    )
                pid = provider.create(record=draft, status=PIDStatus.RESERVED)
                pid_attrs = {
                    "identifier": pid.pid_value,
                    "provider": provider.name,
                }
                if provider.client:
                    pid_attrs["client"] = provider.client.name
                pids[scheme] = pid_attrs

        return pids

    def update(self, identity, draft, pids, errors):
        """Update a list of PIDs based on a draft."""
        updated_pids = dict(draft.get("pids", {}))  # force copy

        for scheme, old_pid in draft.get("pids", {}).items():
            updated_pid = pids.get(scheme)
            if old_pid != updated_pid:
                try:  # record and scheme reach the generator as "over"
                    self.require_permission(
                        identity, 'pid_delete', record=draft, scheme=scheme
                    )

                    # delete if existant in db
                    pid_value = old_pid.get("identifier")
                    if pid_value:  # e.g. remove external and incomplete pid
                        provider = self._get_provider(
                            scheme, old_pid.get("provider")
                        )
                        try:
                            pid = provider.get(pid_value=pid_value)
                            provider.delete(pid, record=draft)
                        except PIDDoesNotExistError:
                            pass  # does not exist, no need to delete it
                    # remove or replace by the new pid
                    updated_pids.pop(scheme, None)
                    if updated_pid:  # an update could be a removal
                        updated_pids[scheme] = updated_pid

                except PermissionDeniedError:
                    errors.append({
                        "field": f"pids.{scheme}",
                        "message": _("Permission denied: cannot update PID.")
                    })
                    continue

        # add new pids to the draft
        new_pids = set(pids.keys()) - set(updated_pids.keys())
        for new_pid in new_pids:
            updated_pids[new_pid] = pids[new_pid]

        return updated_pids

    def reserve(self, draft, pid_attrs, scheme):
        """Reserve a PID."""
        provider = self._get_provider(scheme, pid_attrs["provider"])
        pid = provider.get(pid_attrs["identifier"])
        if pid.is_new():  # not reserved and not registered
            provider.reserve(pid, record=draft)

    def reserve_many(self, draft, pids):
        """Reserve PIDs from a list."""
        for scheme, pid_attrs in pids.items():
            self.reserve(draft, pid_attrs, scheme)

    def register_by_scheme(self, record, scheme):
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
        pid = provider.get(pid_value=pid_value, scheme=scheme)

        links = self.links_item_tpl.expand(record)
        provider.register(
            pid, record=record, url=links["self_html"]
        )

    def discard(self, pid_attrs, scheme):
        """Discard a PID."""
        provider = self._get_provider(scheme, pid_attrs.get("provider"))
        try:
            pid = provider.get(pid_value=pid_attrs["identifier"])
            if pid.is_new():  # pids should be status NEW at this point
                provider.delete(pid)
        except PIDDoesNotExistError:
            pass  # pid was not saved to pidstore yet, no deletion needed

    def discard_by_scheme(self, draft, scheme, pid_provider=None):
        """Discard a PID by the scheme."""
        provider = self._get_provider(scheme, pid_provider)
        try:
            pid_attr = draft.pids[scheme]
            pid = provider.get_by_record(
                draft.id,
                pid_type=scheme,
                pid_value=pid_attr["identifier"],
            )
        # KeyError if the pid is not present in the draft
        # PIDDoesNotExistError if not present in DB
        except (KeyError, PIDDoesNotExistError):
            raise ValidationError(
                message=_("No PID found for scheme {scheme}")
                .format(scheme=scheme),
                field_name=f"pids.{scheme}",
            )

        provider.delete(pid)

    def discard_all(self, pids):
        """Discard all PIDs."""
        for scheme, pid_attrs in pids.items():
            self.discard(pid_attrs, scheme)
