# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
# Copyright (C) 2025-2026 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Database models related to access requests."""

import uuid
from datetime import date, datetime, timezone
from secrets import token_urlsafe

from invenio_db import db
from sqlalchemy_utils import UUIDType

from .permissions import AccessRequestTokenNeed


class AccessRequestToken(db.Model):
    """Token for accessing guest-based access requests.

    These tokens are used in the guest-based access request workflow to
    signify that somebody has requested access to a record via e-mail,
    but hasn't verified their e-mail yet.
    Once the e-mail address is verified to create the access request, this
    the corresponding ``AccessRequestToken`` will be deleted, and a new
    guest access request will be created with some of the token's information.
    """

    __tablename__ = "rdm_records_access_request_tokens"

    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    """Access request token ID."""

    token = db.Column(db.String(512), nullable=False)
    """Randomly generated token which will grant access to the request."""

    created = db.Column(
        db.UTCDateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    """Creation timestamp."""

    expires_at = db.Column(db.UTCDateTime, nullable=False)
    """Expiration date."""

    email = db.Column(db.String(255), nullable=False)
    """E-mail address for which the access request was made."""

    full_name = db.Column(db.String(255), nullable=False, default="")
    """Full name of the requester."""

    message = db.Column(db.Text, nullable=False, default="")
    """Message associated with the request, explaining why access is needed."""

    record_pid = db.Column(db.String(255), nullable=False)
    """PID value of the record for which the request will be created."""

    consent_to_share_personal_data = db.Column(db.String(255), nullable=False)

    def delete(self):
        """Delete this secret link."""
        db.session.delete(self)

    def to_dict(self):
        """Dump the access request token to a dictionary."""
        return {
            "id": str(self.id),
            "token": str(self.token),
            "created_at": self.created,
            "expires_at": self.expires_at,
            "email": self.email,
            "full_name": self.full_name,
            "message": self.message,
            "consent_to_share_personal_data": self.consent_to_share_personal_data,
            "record_pid": self.record_pid,
        }

    @property
    def need(self):
        """Get the needs provided by the link."""
        return AccessRequestTokenNeed(str(self.id))

    @property
    def is_expired(self):
        """Determine if link is expired."""
        return datetime.now(timezone.utc) > self.expires_at

    @classmethod
    def get_by_token(cls, token):
        """Get the AccessRequestToken referenced by the specified token."""
        return cls.query.filter_by(token=token).one_or_none()

    @classmethod
    def create(
        cls,
        email,
        full_name,
        message,
        record_pid,
        shelf_life=None,
        expires_at=None,
        consent=False,
    ):
        """Create a new request access token.

        The ``expires_at`` value will take precedence over the ``shelf_life``.

        :param email: The email address for which the request is made.
        :param full_name: The full name of the requester.
        :param message: The message attached to the request.
        :param record_pid: The PID value for the record that is subject to the request.
        :param shelf_life: The ``timedelta`` for how long the token will live for.
        :param expires_at: The expiration date of the access request token.
        """
        if shelf_life and not expires_at:
            expires_at = datetime.now(timezone.utc) + shelf_life

        is_date = isinstance(expires_at, date)
        is_datetime = isinstance(expires_at, datetime)
        if is_date and not is_datetime:
            expires_at = datetime.combine(expires_at, datetime.min.time())

        access_request_token = cls(
            email=email,
            full_name=full_name,
            message=message,
            record_pid=record_pid,
            expires_at=expires_at,
            token=token_urlsafe(),
            consent_to_share_personal_data=consent,
        )
        db.session.add(access_request_token)

        return access_request_token
