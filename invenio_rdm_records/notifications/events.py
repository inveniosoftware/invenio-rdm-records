# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-Notifications is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Events used for notifications."""

from dataclasses import dataclass
from typing import ClassVar


# taken from event bus implementation.
# only difference is casing, as this is how it is currently defined in the request actions (should be no problem to change it)
# TODO: Move base event to invenio-records-resources
@dataclass
class Event:
    """Base event."""

    type: str
    handling_key: str


@dataclass
class CommunitySubmissionEvent(Event):
    """Community related events."""

    recid: str
    type: ClassVar[str] = "community-submission"
    handling_key: ClassVar[str] = "community-submission"


@dataclass
class CommunitySubmissionSubmittedEvent(CommunitySubmissionEvent):
    """Record related events."""

    action: ClassVar[str] = "submitted"
    handling_key: ClassVar[str] = f"{CommunitySubmissionEvent.type}.{action}"


@dataclass
class CommunitySubmissionDeletedEvent(CommunitySubmissionEvent):
    """Record related events."""

    action: ClassVar[str] = "deleted"
    handling_key: ClassVar[str] = f"{CommunitySubmissionEvent.type}.{action}"


@dataclass
class CommunitySubmissionCreatedEvent(CommunitySubmissionEvent):
    """Record related events."""

    action: ClassVar[str] = "created"
    handling_key: ClassVar[str] = f"{CommunitySubmissionEvent.type}.{action}"


@dataclass
class CommunitySubmissionDeclinedEvent(CommunitySubmissionEvent):
    """Record related events."""

    action: ClassVar[str] = "declined"
    handling_key: ClassVar[str] = f"{CommunitySubmissionEvent.type}.{action}"


@dataclass
class CommunityInvitationEvent(Event):
    """Community related events."""

    recid: str
    type: ClassVar[str] = "community-invitation"
    handling_key: ClassVar[str] = "community-invitation"


@dataclass
class CommunityInvitationCreatedEvent(CommunityInvitationEvent):
    """Record related events."""

    action: ClassVar[str] = "created"
    handling_key: ClassVar[str] = f"{CommunityInvitationEvent.type}.{action}"


@dataclass
class CommunityInvitationAcceptedEvent(CommunityInvitationEvent):
    """Record related events."""

    action: ClassVar[str] = "accepted"
    handling_key: ClassVar[str] = f"{CommunityInvitationEvent.type}.{action}"


@dataclass
class CommunityInvitationDeclinedEvent(CommunityInvitationEvent):
    """Record related events."""

    action: ClassVar[str] = "declined"
    handling_key: ClassVar[str] = f"{CommunityInvitationEvent.type}.{action}"
