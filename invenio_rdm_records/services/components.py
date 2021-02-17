# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM service components."""

from invenio_records_resources.services.records.components import \
    ServiceComponent
from marshmallow import ValidationError


class AccessComponent(ServiceComponent):
    """Service component for access integration."""

    def _validate_record_access(self, record):
        """Check if all entities referenced in record.access do exist."""
        errors = []

        for owner in record.access.owners:
            try:
                owner.resolve(raise_exc=True)
            except LookupError as e:
                errors.append(e)

        for grant in record.access.grants:
            try:
                grant.resolve_subject(raise_exc=True)
            except LookupError as e:
                errors.append(e)

        return errors

    def _populate_access_and_validate(self, identity, data, record, **kwargs):
        """Populate and validate the record's access field."""
        if "access" in data:
            # populate the record's access field with the data already
            # validated by marshmallow
            record.update({"access": data.get("access")})
            record.access.refresh_from_dict(record.get("access"))

        if record is not None and not record.access.owners and identity.id:
            # NOTE: this should not happen, because the jsonschema demands
            #       at least one owner to be specified
            record.access.owners.add({"user": identity.id})

        errors = self._validate_record_access(record)
        errors.extend(record.access.errors)

        if errors:
            # filter out duplicate error messages
            messages = list({str(e) for e in errors})
            raise ValidationError(messages, field_name="access")

    def create(self, identity, data=None, record=None, **kwargs):
        """Add basic ownership fields to the record."""
        self._populate_access_and_validate(identity, data, record, **kwargs)

    def update(self, identity, data=None, record=None, **kwargs):
        """Update handler."""
        self._populate_access_and_validate(identity, data, record, **kwargs)
