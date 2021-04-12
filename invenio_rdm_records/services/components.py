# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM service components."""

from copy import copy

from flask_babelex import lazy_gettext as _
from invenio_access.permissions import system_process
from invenio_pidstore.models import PIDStatus
from invenio_records_resources.services.records.components import \
    ServiceComponent
from marshmallow import ValidationError


class ParentRecordAccessComponent(ServiceComponent):
    """Service component for access integration in parent records."""

    def _validate_record_access(self, record):
        """Check if all entities referenced in record.access do exist."""
        parent = record
        errors = []

        for owner in parent.access.owners:
            try:
                owner.resolve(raise_exc=True)
            except LookupError as e:
                errors.append(e)

        for grant in parent.access.grants:
            try:
                grant.resolve_subject(raise_exc=True)
            except LookupError as e:
                errors.append(e)

        return errors

    def _populate_access_and_validate(self, identity, data, record, **kwargs):
        """Populate and validate the parent record's access field."""
        parent = record
        if parent is not None and "access" in data:
            parent.update({"access": data.get("access")})
            parent.access.refresh_from_dict(parent.get("access"))

        errors = parent.access.errors
        if errors:
            messages = list({str(e) for e in errors})
            raise ValidationError(messages, field_name="access")

    def create(self, identity, data=None, record=None, **kwargs):
        """Add basic ownership fields to the parent."""
        self._populate_access_and_validate(identity, data, record, **kwargs)

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Update handler."""
        self._populate_access_and_validate(identity, data, record, **kwargs)


class AccessComponent(ServiceComponent):
    """Service component for access integration."""

    def _populate_access_and_validate(self, identity, data, record, **kwargs):
        """Populate and validate the record's access field."""
        if record is not None and "access" in data:
            # populate the record's access field with the data already
            # validated by marshmallow
            record.update({"access": data.get("access")})
            record.access.refresh_from_dict(record.get("access"))

        errors = record.access.errors
        if errors:
            # filter out duplicate error messages
            messages = list({str(e) for e in errors})
            raise ValidationError(messages, field_name="access")

    def _init_owners(self, identity, record, **kwargs):
        """If the record has no owners yet, add the current user."""
        # if the given identity is that of a user, we add the
        # corresponding user to the owners
        # (record.parent.access.owners) and commit the parent
        # otherwise, the parent's owners stays empty
        is_sys_id = system_process in identity.provides
        if not record.parent.access.owners and not is_sys_id:
            owner_dict = {"user": identity.id}
            record.parent.access.owners.add(owner_dict)
            record.parent.commit()

    def create(self, identity, data=None, record=None, **kwargs):
        """Add basic ownership fields to the record."""
        self._populate_access_and_validate(identity, data, record, **kwargs)
        self._init_owners(identity, record, **kwargs)

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Update handler."""
        self._populate_access_and_validate(identity, data, record, **kwargs)

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        record.access = draft.access

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        draft.access = record.access

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        draft.access = record.access


class MetadataComponent(ServiceComponent):
    """Service component for metadata."""

    new_version_skip_fields = ['publication_date', 'version']

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject parsed metadata to the record."""
        record.metadata = data.get('metadata', {})

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Inject parsed metadata to the record."""
        record.metadata = data.get('metadata', {})

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        record.metadata = draft.get('metadata', {})

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        draft.metadata = record.get('metadata', {})

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        draft.metadata = copy(record.get('metadata', {}))
        # Remove fields that should not be copied to the new version
        # (publication date and version)
        for f in self.new_version_skip_fields:
            draft.metadata.pop(f, None)


class ExternalPIDsComponent(ServiceComponent):
    """Service component for pids."""

    def get_provider(self, scheme):
        """Process a given PID with its provider."""
        provider = self.service.config.pids_providers[scheme]

        return provider

    def _validate_pids(self, pids):
        """Validate an iterator of pids."""
        for scheme, pid_attrs in pids.items():
            self.get_provider(scheme).validate(pid_attrs=pid_attrs)

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject parsed pids to the record."""
        pids = data.get('pids', {})
        self._validate_pids(pids)
        record.pids = pids

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Inject parsed pids to the record."""
        pids = data.get('pids', {})
        self._validate_pids(pids)
        record.pids = pids

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft pids."""
        pids = draft.get('pids', {})

        for scheme, pid_attrs in pids.items():
            provider = self.get_provider(scheme)
            provider.validate(pid_attrs=pid_attrs)

            identifier_value = pid_attrs.get("identifier")
            if not identifier_value:
                pid = provider.create()
                pid_attrs["identifier"] = pid.value
                pids[scheme] = pid_attrs

            elif not provider.is_external():
                raise ValidationError(
                    _(f"Cannot create PID {scheme} with a given value," +
                      "it must be assigned by the system."),
                    field_name="pids"
                )
            else:
                pid = provider.get(identifier_value)

            # PIDS-FIXME: Move to provier.validate base class?
            if pid.status != PIDStatus.RESERVED != PIDStatus.REGISTERED:
                provider.reserve(pid)

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Update draft pids."""
        # NOTE: getting from record instead of draft
        # Do not allow to edit pids
        pids = record.get('pids', {})
        self._validate_pids(pids)
        record.pids = pids

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft pids."""
        pids = record.get('pids', {})

        # PIDS-FIXME: Remove DOI (maybe all)
        # new version should be no PIDS just concept?
        self._validate_pids(pids)
        record.pids = pids
