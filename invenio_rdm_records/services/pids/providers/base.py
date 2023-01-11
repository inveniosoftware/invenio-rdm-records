# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PID Provider."""

from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_pidstore.errors import PIDAlreadyExists, PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus


class PIDProvider:
    """Base class for PID providers."""

    def __init__(
        self,
        name,
        client=None,
        pid_type=None,
        default_status=PIDStatus.NEW,
        managed=True,
        label=None,
        *kwargs,
    ):
        """Constructor."""
        self.name = name
        self.label = label or name
        self.client = client
        self.pid_type = pid_type
        self.default_status = default_status
        self.managed = managed

    def generate_id(self, record, **kwargs):
        """Generates an identifier value."""
        raise NotImplementedError

    def is_managed(self):
        """Determine if the provider is managed or unmanaged.

        Managed providers auto-generate identifiers, while unmanaged providers
        a user must supply it with the identifier value.
        """
        return self.managed

    def can_modify(self, pid, **kwargs):
        """Checks if the given PID can be modified."""
        return True

    def get(self, pid_value, pid_provider=None):
        """Get a persistent identifier for this provider.

        :param pid_type: Persistent identifier type.
        :param pid_value: Persistent identifier value.
        :returns: A :class:`invenio_pidstore.models.base.PersistentIdentifier`
            instance.x
        """
        args = {"pid_type": self.pid_type, "pid_value": pid_value}
        if pid_provider:
            # FIXME: should be pid_provider or self.name?
            args["pid_provider"] = pid_provider

        return PersistentIdentifier.get(**args)

    def create(self, record, pid_value=None, status=None, **kwargs):
        """Get or create the PID with given value for the given record.

        :param record: the record to create the PID for.
        :param value: the PID value.
        :returns: A :class:`invenio_pidstore.models.base.PersistentIdentifier`
            instance.
        """
        if pid_value is None:
            if not self.is_managed():
                raise ValueError("You must provide a pid value.")
            pid_value = self.generate_id(record)

        try:
            pid = self.get(pid_value)
        except PIDDoesNotExistError:
            # not existing, create a new one
            return PersistentIdentifier.create(
                self.pid_type,
                pid_value,
                pid_provider=self.name,
                object_type="rec",
                object_uuid=record.id,
                status=status or self.default_status,
            )

        # re-activate if previously deleted
        if pid.is_deleted():
            pid.sync_status(PIDStatus.NEW)
            return pid
        else:
            raise PIDAlreadyExists(self.pid_type, pid_value)

    def reserve(self, pid, **kwargs):
        """Reserve a persistent identifier.

        This might or might not be useful depending on the service of the
        provider.

        See: :meth:`invenio_pidstore.models.PersistentIdentifier.reserve`.
        """
        is_reserved_or_registered = pid.is_reserved() or pid.is_registered()
        if not is_reserved_or_registered:
            return pid.reserve()
        return True

    def register(self, pid, **kwargs):
        """Register a persistent identifier.

        See: :meth:`invenio_pidstore.models.PersistentIdentifier.register`.
        """
        if not pid.is_registered():
            return pid.register()
        return True

    def update(self, pid, **kwargs):
        """Update information about the persistent identifier."""
        pass

    def delete(self, pid, **kwargs):
        """Delete a persistent identifier.

        See: :meth:`invenio_pidstore.models.PersistentIdentifier.delete`.
        """
        return pid.delete()

    def validate(self, record, identifier=None, provider=None, **kwargs):
        """Validate the attributes of the identifier.

        :returns: A tuple (success, errors). `success` is a bool that specifies
                  if the validation was successful. `errors` is a list of
                  error dicts of the form:
                  `{"field": <field>, "messages: ["<msgA1>", ...]}`.
        """
        if provider and provider != self.name:
            current_app.logger.error(
                "Configuration error: provider "
                f"name {provider} does not match "
                f"{self.name}."
            )
            raise  # configuration error

        # deduplication check
        try:
            pid = self.get(pid_value=identifier)
            if pid.object_uuid != record.id:
                current_app.logger.warning(
                    f"PID {self.pid_type}:{identifier} already exists"
                )
                return False, [
                    # Note that this uses self.pid_type which is not dynamically
                    # assigned from config.py::RDM_PERSISTENT_IDENTIFIERS, so there
                    # may come a time where there is a mismatch between the two.
                    {
                        "field": f"pids.{self.pid_type}",
                        "messages": [
                            _("{pid_type}:{identifier} already exists.").format(
                                pid_type=self.pid_type, identifier=identifier
                            )
                        ],
                    }
                ]
        except PIDDoesNotExistError:
            pass

        return True, []

    def _insert_pid_type_error_msg(self, errors, error_msg):
        """Adds error_msg to "messages" field of pid_type's error_dict in errors.

        This error dict is either:
        - retrieved from errors OR
        - created and appended to errors

        This is really a utility method for children providers in order
        to append pid identifier error messages to the pid identifier error_dict
        (as opposed to creating a new error dict).

        :param errors: list of error dicts of the form `{"field": ..., "messages": ...}`
        :param error_msg: string OR list of strings
        """
        field = f"pids.{self.pid_type}"
        error = next((error for error in errors if error.get("field") == field), None)

        if not error:
            error = {"field": field, "messages": []}
            errors.append(error)

        if isinstance(error_msg, list):
            error["messages"].extend(error_msg)
        else:
            error["messages"].append(error_msg)
