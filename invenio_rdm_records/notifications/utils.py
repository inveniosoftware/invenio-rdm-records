from invenio_access.permissions import system_identity
from invenio_communities.members.records.api import Member
from invenio_communities.proxies import current_communities
from invenio_records_resources.notifications import (
    BackendPayloadGenerator,
    NotificationBuilder,
    PayloadGenerator,
    RecipientGenerator,
)
from invenio_requests import current_requests_service
from invenio_users_resources.notifications import UserPreferencesRecipientFilter

from invenio_rdm_records.proxies import current_rdm_records_service

from .events import CommunitySubmissionSubmittedEvent


# NOTE: Move to invenio-records-resources?
class BaseRecordPayloadGenerator(PayloadGenerator):
    """Record payload for a notification."""

    # NOTE: Since we want links and everything resolved, we should use a result item from the service level.
    def __init__(self, key, record_item, **kwargs):
        """Ctor."""
        self._record_item = record_item
        self._key = key

    def run(self, **kwargs):
        """Creates a serializable payload from the record."""
        return {self._key: self._record_item.to_dict()}


class RDMRecordPayloadGenerator(BaseRecordPayloadGenerator):
    """Record payload for a notification."""

    def __init__(self, record_item, **kwargs):
        """Ctor."""
        super().__init__("record", record_item, **kwargs)


# NOTE: Move to invenio-communities?
class CommunityPayloadGenerator(BaseRecordPayloadGenerator):
    """Community payload for a notification."""

    def __init__(self, record_item, **kwargs):
        """Ctor."""
        super().__init__("community", record_item, **kwargs)


# NOTE: Move to invenio-requests?
class RequestPayloadGenerator(BaseRecordPayloadGenerator):
    """Request payload for a notification."""

    def __init__(self, record_item, **kwargs):
        """Ctor."""
        super().__init__("request", record_item, **kwargs)


class CommunityRecipientGenerator(RecipientGenerator):
    """Communit recipient generator for a notification."""

    def __init__(self, community, **kwargs):
        """Ctor."""
        self._community = community

    def run(self, payload, **kwargs):
        """Generate recipients."""
        members = Member.get_members(self._community.id)
        # TODO: check if this .dereference generates same dump as the user dump.
        #       if not, will have to look up users by their id
        return [m.relations.user.dereference() for m in members if m.user_id]


# NOTE: Move to specific backend?
class EMailBackendPayloadGenerator(BackendPayloadGenerator):
    """Backend generator for the email backend."""

    backend_id = "email"

    def __init__(self, template):
        super().__init__()
        self.template = template

    def run(self, user, **kwargs):
        """Generate backend payload."""
        payload = {
            **super().run(user, **kwargs),
            "to": user.get("email", ""),
        }

        return payload


class CommunitySubmissionNotificationBuilder(NotificationBuilder):
    type = CommunitySubmissionSubmittedEvent.handling_key

    # NOTE: Should we only pass ids and then read entities as needed or already pass
    #       the result item of a service level read?
    #       Then we would have the identity check as well.
    def __init__(self, trigger, record, community, request):
        super().__init__(trigger)
        self._record = record
        self._community = community
        self._request = request

        read_record = (
            current_rdm_records_service.read
            if record.is_published
            else current_rdm_records_service.read_draft
        )

        # NOTE: accessing id is not consistent. See note above for possible fix
        self.payload_generators = [
            RDMRecordPayloadGenerator(
                record_item=read_record(system_identity, self._record["id"])
            ),
            CommunityPayloadGenerator(
                record_item=current_communities.service.read(
                    system_identity, self._community.id
                )
            ),
            RequestPayloadGenerator(
                record_item=current_requests_service.read(
                    system_identity, self._request.id
                )
            ),
        ]
        self.recipients_generators = [
            CommunityRecipientGenerator(community=self._community),
        ]

        # TODO: Uncomment before merging. Just to make testing easier
        self.recipients_filters = [
            # UserPreferencesRecipientFilter(),
        ]

        self.backend_payload_generators = [
            EMailBackendPayloadGenerator(
                template=self.type,
            ),
        ]
        self.recipient_backend_transforms = []


class CommunitySubmissionSubmittedNotificationBuilder(
    CommunitySubmissionNotificationBuilder
):
    type = CommunitySubmissionSubmittedEvent.handling_key
