# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Recipient generators for notifications."""

from invenio_access.permissions import system_identity
from invenio_notifications.models import Recipient
from invenio_notifications.services.generators import RecipientGenerator
from invenio_records.dictutils import dict_lookup
from invenio_users_resources.proxies import current_users_service


class RecordManagersRecipient(RecipientGenerator):
    """Adds users with explicit manage grants on the topic record as recipients."""

    def __init__(self, key):
        """Constructor."""
        self.key = key

    def __call__(self, notification, recipients):
        """Fetch record and add record managers as recipients."""
        from invenio_rdm_records.records.api import RDMRecord
        from invenio_rdm_records.services.generators import AccessGrant

        topic = dict_lookup(notification.context, self.key)
        record = RDMRecord.pid.resolve(topic["id"])

        manager_needs = AccessGrant("manage").needs(record=record)
        user_ids = {str(n.value) for n in manager_needs if n.method == "id"}

        for user_id in user_ids:
            if user_id in recipients:
                continue
            user = current_users_service.read(system_identity, user_id)
            recipients[user_id] = Recipient(data=user.data)

        return recipients
