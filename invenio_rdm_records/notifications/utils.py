from invenio_communities.members.records.api import Member
from invenio_records_resources.notifications import (
    NotificationBuilder,
    PayloadGenerator,
    RecipientGenerator,
)
from invenio_users_resources.notifications import (
    UserPreferencesRecipientFilter,
)

from .events import CommunitySubmissionEvent, CommunitySubmissionSubmittedEvent


# NOTE: Move to invenio-records-resources?
#       Generalize further to take a key and a record object, which gets dumped?
class RecordPayloadGenerator(PayloadGenerator):
    """Record payload for a notification."""

    def __init__(self, record, **kwargs):
        """Ctor."""
        self._record = record

    def run(self, **kwargs):
        """Creates a serializable payload from the record."""
        return {"record": self._record.dumps()}


# NOTE: Move to invenio-communities?
class CommunityPayloadGenerator(PayloadGenerator):
    """Community payload for a notification."""

    def __init__(self, community, **kwargs):
        """Ctor."""
        self._community = community

    def run(self, **kwargs):
        """Creates a serializable payload from the community."""
        return {"community": self._community.dumps()}


# NOTE: Move to invenio-requests?
class RequestPayloadGenerator(PayloadGenerator):
    """Request payload for a notification."""

    def __init__(self, request, **kwargs):
        """Ctor."""
        self._request = request

    def run(self, **kwargs):
        """Creates a serializable payload from the request."""
        return {"request": self._request.dumps()}


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


class CommunitySubmissionNotificationBuilder(NotificationBuilder):
    type = CommunitySubmissionEvent.handling_key

    def __init__(self, trigger, record, community, request):
        super().__init__(trigger)
        self._record = record
        self._community = community
        self._request = request

        self.payload_generator = [
            RecordPayloadGenerator(record=self._record),
            CommunityPayloadGenerator(community=self._community),
            RequestPayloadGenerator(request=self._request),
        ]
        self.recipients_generator = [
            CommunityRecipientGenerator(community=self._community),
        ]
        self.recipients_filters = [
            # UserPreferencesRecipientFilter(),
        ]
        self.recipient_backend_transform = []


class CommunitySubmissionSubmittedNotificationBuilder(
    CommunitySubmissionNotificationBuilder
):
    type = CommunitySubmissionSubmittedEvent.handling_key
