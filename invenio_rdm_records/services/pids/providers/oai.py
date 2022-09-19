# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OAI ID PID Provider."""

from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_pidstore.models import PIDStatus

from .base import PIDProvider


class OAIPIDProvider(PIDProvider):
    """OAI ID PID Provider."""

    name = "oai"

    def __init__(self, name, **kwargs):
        """Constructor."""
        super().__init__(
            name,
            pid_type="oai",
            default_status=PIDStatus.REGISTERED,
            managed=True,
            **kwargs,
        )

    def generate_id(self, record, **kwargs):
        """Generates an identifier value."""
        # http://www.openarchives.org/OAI/2.0/guidelines-oai-identifier.htm
        prefix = current_app.config.get("OAISERVER_ID_PREFIX", "")
        return f"oai:{prefix}:{record.pid.pid_value}"

    def reserve(self, pid, record, **kwargs):
        """Constant True.

        PID default status is registered.
        """
        return True
