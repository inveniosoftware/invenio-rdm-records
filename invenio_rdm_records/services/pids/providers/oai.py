# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PID Base Provider."""

from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PIDStatus

from .base import BaseClient, BasePIDProvider


class OAIPIDClient(BaseClient):
    """OAI Client.

    Loads the value from config.
    """

    def __init__(self, name, url=None, config_key=None, **kwargs):
        """Constructor."""
        super().__init__(name, None, None, url=url, **kwargs)

        # TODO: OAISERVER_ID_PREFIX already has oai: at the beginning.
        # guess this should be removed and only the domain name should remain?
        self.prefix = current_app.config.get('OAISERVER_ID_PREFIX', '')


class OAIPIDProvider(BasePIDProvider):
    """OAI Provider class."""

    name = "oai"

    def _generate_id(self, record, **kwargs):
        """Generates an identifier value."""
        pid_value = record.pid.pid_value

        # http://www.openarchives.org/OAI/2.0/guidelines-oai-identifier.htm
        identifier = f"oai:{self.client.prefix}:{pid_value}"

        return identifier

    def __init__(
        self,
        client,
        pid_type="oai",
        default_status=PIDStatus.REGISTERED,
        system_managed=True,
        required=True,
        **kwargs,
    ):
        """Constructor."""
        self.client = client
        super().__init__(
            pid_type=pid_type,
            default_status=default_status,
            system_managed=system_managed,
            required=required,
        )

    def create(self, record, **kwargs):
        """Get or create OAI PID.

        Get OAI PID for existing record or create a new unique
        OAI PID based on the record ID.
        """
        oai_pid = self._generate_id(record, **kwargs)

        try:
            pid = super().get(pid_value=oai_pid)
        except PIDDoesNotExistError:
            pid = super().create(record=record, value=oai_pid)

        return pid

    def reserve(self, pid, record, **kwargs):
        """Constant True.

        PID default status is registered.
        """
        return True
