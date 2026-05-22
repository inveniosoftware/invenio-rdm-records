# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""RDM service component for Software Heritage integration."""

from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_records_resources.services.uow import TaskOp

from invenio_rdm_records.services.tasks import send_post_published_signal


class SignalComponent(ServiceComponent):
    """Service component to trigger signals on publish."""

    def publish(self, identity, draft=None, record=None):
        """Publish record."""
        self.uow.register(TaskOp(send_post_published_signal, pid=record["id"]))
