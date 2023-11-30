# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""RDM service component for Software Heritage integration."""

from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_records_resources.services.uow import TaskOp

from invenio_rdm_records.services.tasks import send_post_published_signal


class SignalComponent(ServiceComponent):
    """Service component to trigger signals on publish."""

    def publish(self, identity, draft=None, record=None):
        """Publish record."""
        self.uow.register(TaskOp(send_post_published_signal, pid=record["id"]))
