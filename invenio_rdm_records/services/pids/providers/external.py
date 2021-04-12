# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PID Base Provider."""

from invenio_pidstore.models import PIDStatus

from .base import BaseProvider


class ExternalProvider(BaseProvider):
    """This provider is validates PIDs to external contraints.

    It does not support any other type of operation. However, it helps
    generalize the service code by using polymorphism.
    """

    def __init__(self, name="external", **kwargs):
        """Constructor."""
        super(ExternalProvider, self).__init__(
            name=name, system_managed=False)

    def get(self, pid_value, pid_type=None, **kwargs):
        """Not allowed for external PIDs."""
        raise NotImplementedError

    def create(self, pid_value=None, pid_type=None, object_type=None,
               object_uuid=None, **kwargs):
        """Not allowed for external PIDs."""
        raise NotImplementedError

    def reserve(self, pid, **kwargs):
        """Not allowed for external PIDs."""
        raise NotImplementedError

    def register(self, pid, **kwargs):
        """Not allowed for external PIDs."""
        raise NotImplementedError

    def update(self, pid, **kwargs):
        """Not allowed for external PIDs."""
        raise NotImplementedError

    def delete(self, pid, **kwargs):
        """Not allowed for external PIDs."""
        raise NotImplementedError

    def get_status(self, identifier, **kwargs):
        """Not allowed for external PIDs."""
        raise NotImplementedError

    def validate(self, pid_attrs, **kwargs):
        """Validate the attributes of the identifier."""
        # PIDS-FIXME: implement (e.g. attrs cannot have client)
        # Old code from the validate-pids in the schemais_provider_external = \
        # pid_attrs.get("provider") == PID_PROVIDER_EXTERNAL
        # has_client = pid_attrs.get("client")
        # if is_provider_external and has_client:
        #     raise ValidationError(
        #         _("External provider cannot have a client."),
        #         field_name="pids",
        #     )
        return True
