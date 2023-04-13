from invenio_access.permissions import system_identity
from invenio_communities.communities.records.api import Community
from invenio_communities.proxies import current_communities
from invenio_notifications.models import Notification
from invenio_notifications.registry import EntityResolverRegistry
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.generators import EntityResolve
from invenio_users_resources.notifications import UserEmailBackend, UserRecipient

from .events import CommunityInclusionSubmittedEvent


class CommunityMembersRecipient:
    def __init__(self, key, roles=None):
        self.key = key
        self.roles = roles

    def __call___(self, notification, recipients: list):
        community = notification[self.key]
        if isinstance(community, Community):
            members = current_communities.service.members.search(
                system_identity,
                community["id"],
                roles=self.roles,
            )
            for m in members:
                if not m.user_id:
                    continue
                if self.roles and m.role not in self.roles:
                    continue
                user = m.relations.user.dereference()
                # notif_pref = user.preferences["notifications"]
                # com_pref = notif_pref.get(community.id)
                # if com_pref:
                #     # check if notification is enabled/disabled for the member
                #     # if ...:
                #     #     continue
                recipients.append(user)
        return recipients


class CommunityInclusionNotificationBuilder(NotificationBuilder):
    type = CommunityInclusionSubmittedEvent.handling_key

    @classmethod
    def build(cls, request):
        return Notification(
            type=cls.type,
            context=EntityResolverRegistry.reference_entity(request),
        )

    context = [
        EntityResolve(key="request"),
        EntityResolve(key="request.created_by"),
        EntityResolve(key="request.topic"),
        EntityResolve(key="request.receiver"),
    ]

    recipients = [
        CommunityMembersRecipient(key="request.receiver", roles=["curator", "owner"]),
        UserRecipient(key="request.created_by"),
    ]

    recipient_filters = []

    recipient_backends = [
        UserEmailBackend(),
    ]


class CommunityInclusionSubmittedNotificationBuilder(
    CommunityInclusionNotificationBuilder
):
    type = CommunityInclusionSubmittedEvent.handling_key
