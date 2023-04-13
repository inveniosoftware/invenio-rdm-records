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
    action: str
    handling_key: str = f"{type}.{action}"


@dataclass
class CommunityRecordInclusionEvent(Event):
    """Community related events."""

    type = "community-submission"
    action = ""


@dataclass
class CommunityInclusionSubmittedEvent(CommunityRecordInclusionEvent):
    """Record related events."""

    action: ClassVar[str] = "submitted"


@dataclass
class CommunityInclusionDeclinedEvent(CommunityRecordInclusionEvent):
    """Record related events."""

    action: ClassVar[str] = "declined"


@dataclass
class CommunityInvitationEvent(Event):
    """Community related events."""

    type: ClassVar[str] = "community-invitation"


@dataclass
class CommunityInvitationCreatedEvent(CommunityInvitationEvent):
    """Record related events."""

    action: ClassVar[str] = "created"


@dataclass
class CommunityInvitationAcceptedEvent(CommunityInvitationEvent):
    """Record related events."""

    action: ClassVar[str] = "accepted"


@dataclass
class CommunityInvitationDeclinedEvent(CommunityInvitationEvent):
    """Record related events."""

    action: ClassVar[str] = "declined"