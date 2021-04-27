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

from invenio_access.permissions import system_process
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

    def _validate_pids(self, pids):
        """Validate an iterator of pids."""
        for scheme, pid_attrs in pids.items():
            client = pid_attrs.get("client")
            provider = self.service.get_provider(scheme, client)
            provider.validate(**pid_attrs)

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject parsed pids to the draft record."""
        pids = data.get('pids', {})
        self._validate_pids(pids)
        # NOTE: record is a draft because we hook to the draft service.
        record.pids = pids

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Inject parsed pids to the record."""
        pids = data.get('pids', {})
        self._validate_pids(pids)
        record.pids = pids

    def _publish_managed(
        self, provider, is_required, draft_pid, record_pids, draft=None,
        scheme=None
    ):
        """Publish a system managed PID."""
        identifier_value = draft_pid.get("identifier")
        pid = None
        if is_required:
            if not identifier_value:
                pid = provider.create(draft)
                provider.reserve(pid, draft)
            else:
                pid = provider.get(identifier_value)
                assert pid.is_reserved() or pid.is_registered()

            if not pid.is_registered():  # avoid dup registration
                url = self.service.links_item_tpl.expand(draft)["record"]
                provider.register(pid, draft, url)
            else:
                # PIDS-FIXME: this should update meta to datacite
                pass
        else:
            if identifier_value:
                # must be already created and reserved
                pid = provider.get(identifier_value)
                assert pid.is_reserved() or pid.is_registered()
                # PIDS-FIXME: this should update meta to datacite???
                provider.register(pid, draft)

        if pid:  # ignore not required & no given id value
            record_pids[scheme] = {
                "identifier": pid.pid_value,
                "provider": provider.name,
                "client": provider.client.name
            }

    def _publish_unmanaged(
        self, provider, is_required, draft_pid, record_pids, draft=None,
        scheme=None
    ):
        """Publish an unmanaged PID."""
        identifier_value = draft_pid.get("identifier")
        scheme = provider.pid_type

        if identifier_value:
            record_pids[scheme] = {
                "identifier": identifier_value,
                "provider": provider.name,
            }
        elif draft_pid != {}:
            # NOTE: Do not accept partial
            raise ValidationError(
                f"Value required for {scheme} PID.",
                field_name=f"pids.{scheme}")

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft pids."""
        record_pids = {}
        draft_pids = draft.get('pids', {})
        providers = self.service.get_configured_providers()

        for scheme, provider_config in providers.items():
            # PID content
            draft_pid = draft_pids.get(scheme, {})
            # Provider checks
            client = draft_pid.get("client")
            provider = self.service.get_provider(scheme, client)
            provider.validate(**draft_pid)
            # Publishing part
            # PIDS-FIXME should we require this two config values?
            is_required = provider_config.get("required", False)
            is_system_managed = \
                provider_config.get("system_managed", False)

            if is_system_managed:
                self._publish_managed(
                    provider, is_required, draft_pid, record_pids, draft=draft,
                    scheme=scheme or provider.pid_type)
            else:
                self._publish_unmanaged(
                    provider, is_required, draft_pid, record_pids)

        record.pids = record_pids

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Update draft pids."""
        # PIDS are taken from the published record so that cannot
        # be changed in the draft.
        record_pids = record.get('pids', {})
        self._validate_pids(record_pids)
        draft.pids = record_pids

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft pids."""
        draft.pids = {}
