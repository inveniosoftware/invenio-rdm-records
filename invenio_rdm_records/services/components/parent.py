# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2020 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM service component for access integration in parent records."""


from invenio_drafts_resources.services.records.components import \
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
