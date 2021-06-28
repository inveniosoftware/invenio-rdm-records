# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PID Base Provider."""

from flask import current_app

from .base import BasePIDProvider


class UnmanagedPIDProvider(BasePIDProvider):
    """This provider is validates PIDs to unmanaged constraints.

    It does not support any other type of operation. However, it helps
    generalize the service code by using polymorphism.
    """

    name = "external"

    def __init__(self, pid_type, **kwargs):
        """Constructor."""
        super().__init__(pid_type=pid_type, system_managed=False)

    def create(self, record, value, **kwargs):
        """Create PID."""
        return super().create(record, value)

    def reserve(self, pid, record, **kwargs):
        """Not allowed for unmanaged PIDs."""
        raise NotImplementedError

    def register(self, pid, record, **kwargs):
        """Register PID."""
        return super().register(pid, record)

    def update(self, pid, record, **kwargs):
        """Not allowed for unmanaged PIDs."""
        raise NotImplementedError

    def delete(self, pid, record, **kwargs):
        """Delete PID."""
        return pid.delete()

    def get_status(self, identifier, **kwargs):
        """Not allowed for unmanaged PIDs."""
        return self.get(identifier, **kwargs).status

    def validate(
        self, record, identifier=None, client=None, provider=None, **kwargs
    ):
        """Validate the attributes of the identifier.

        :returns: A tuple (success, errors). The first specifies if the
                  validation was passed successfully. The second one is an
                  array of error messages.
        """
        if client:
            current_app.error("Configuration error: client attribute not "
                              f"supported for provider {self.name}")
            raise  # configuration error

        success, errors = super().validate(
            record, identifier, provider, client, **kwargs)

        return (True, []) if not errors else (False, errors)
