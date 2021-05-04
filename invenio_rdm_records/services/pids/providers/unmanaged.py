# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PID Base Provider."""

from flask_babelex import lazy_gettext as _
from invenio_pidstore.models import PIDStatus

from .base import BasePIDProvider


class UnmanagedPIDProvider(BasePIDProvider):
    """This provider is validates PIDs to unmanaged contraints.

    It does not support any other type of operation. However, it helps
    generalize the service code by using polymorphism.
    """

    name = "unmanaged"

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(pid_type=self.name, system_managed=False)

    def get(self, pid_value, pid_type=None, **kwargs):
        """Not allowed for unmanaged PIDs."""
        raise NotImplementedError

    def create(self, pid_value=None, pid_type=None, object_type=None,
               object_uuid=None, **kwargs):
        """Not allowed for unmanaged PIDs."""
        raise NotImplementedError

    def reserve(self, pid, record, **kwargs):
        """Not allowed for unmanaged PIDs."""
        raise NotImplementedError

    def register(self, pid, record, **kwargs):
        """Not allowed for unmanaged PIDs."""
        raise NotImplementedError

    def update(self, pid, record, **kwargs):
        """Not allowed for unmanaged PIDs."""
        raise NotImplementedError

    def delete(self, pid, record, **kwargs):
        """Not allowed for unmanaged PIDs."""
        raise NotImplementedError

    def get_status(self, identifier, **kwargs):
        """Not allowed for unmanaged PIDs."""
        raise NotImplementedError

    def validate(self, identifier=None, client=None, provider=None, **kwargs):
        """Validate the attributes of the identifier.

        :returns: A tuple (success, errors). The first specifies if the
                  validation was passed successfully. The second one is an
                  array of error messages.
        """
        success, errors = super().validate(provider=provider)

        if client:
            errors.append(
                _(f"Client attribute not supported for provider {self.name}"))

        return (True, []) if not errors else (False, errors)
