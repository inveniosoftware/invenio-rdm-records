# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Secret links for sharing access to records."""

import uuid
from datetime import date, datetime, timezone

from invenio_db import db
from sqlalchemy_utils import UUIDType

from .errors import InvalidPermissionLevelError
from .permissions import LinkNeed
from .serializers import SecretLinkSerializer, TimedSecretLinkSerializer
from .signals import link_created, link_revoked

SUPPORTED_DIGEST_ALGORITHMS = ("HS256", "HS512")


class SecretLink(db.Model):
    """Secret links for sharing permissions on records."""

    __tablename__ = "rdm_records_secret_links"

    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    """Secret link ID."""

    token = db.Column(db.Text, nullable=False)
    """Secret token for link.

    In contrast to Zenodo-AccessRequests, we don't store encrypted tokens, to
    enable querying the SecretLink table by tokens and improve performance.
    In case that the database is leaked, all secret links should be revoked.
    """

    created = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    """Creation timestamp."""

    expires_at = db.Column(db.UTCDateTime, nullable=True)
    """Expiration date."""

    permission_level = db.Column(db.String, nullable=False, default="")
    """Permission level of the link."""

    origin = db.Column(db.String(255), nullable=False, default="N/A")
    """Origin information for the secret link."""

    description = db.Column(db.Text, nullable=False, default="")
    """Description of the secret link, for identification purposes."""

    def revoke(self):
        """Revoke (i.e. delete) this secret link."""
        db.session.delete(self)
        link_revoked.send(self)

    def to_dict(self):
        """Dump the SecretLink to a dictionary."""
        result_dict = {
            "id": str(self.id),
            "token": str(self.token),
            "created_at": self.created,
            "expires_at": self.expires_at,
            "permission": self.permission_level,
            "description": self.description,
        }

        return result_dict

    @property
    def need(self):
        """Get the needs provided by the link."""
        return LinkNeed(str(self.id))

    @property
    def extra_data(self):
        """Load token data stored in token (ignores expiry date of tokens)."""
        if self.token:
            return self.load_token(self.token, force=True)["data"]

        return None

    @property
    def is_expired(self):
        """Determine if link is expired."""
        if self.expires_at:
            return datetime.now(timezone.utc) > self.expires_at

        return False

    @classmethod
    def get_by_token(cls, token):
        """Get the SecretLink referenced by the specified token."""
        data = cls.load_token(token)
        if data:
            link = cls.query.get(data["id"])
            return link
        else:
            return None

    @classmethod
    def create(
        cls,
        permission_level,
        extra_data=None,
        expires_at=None,
        origin=None,
        description=None,
    ):
        """Create a new secret link."""
        if permission_level not in ["view", "preview", "edit"]:
            raise InvalidPermissionLevelError(permission_level)
        is_date = isinstance(expires_at, date)
        is_datetime = isinstance(expires_at, datetime)
        if is_date and not is_datetime:
            expires_at = datetime.combine(expires_at, datetime.min.time())

        if expires_at is None:
            serializer = SecretLinkSerializer()
        else:
            serializer = TimedSecretLinkSerializer(expires_at=expires_at)

        id_ = uuid.uuid4()
        link = cls(
            id=id_,
            permission_level=permission_level,
            expires_at=expires_at,
            token=serializer.create_token(id_, extra_data or {}),
            origin=origin,
            description=description,
        )
        db.session.add(link)
        link_created.send(link)

        return link

    @classmethod
    def validate_token(cls, token, expected_data):
        """Validate a secret link token.

        Only queries the database if token is valid to determine that the token
        has not been revoked.
        """
        data = cls.load_token(token, expected_data=expected_data)

        if data:
            link = cls.query.get(data["id"])
            if link and not link.is_expired:
                return True

        return False

    @staticmethod
    def load_token(token, expected_data=None, force=False):
        """Validate a secret link token (non-expiring + expiring).

        If ``expected_data`` is supplied, its presence in the token will be
        required in order for the token to be considered valid.
        If ``force`` is set to ``True``, the token's expiration date is
        ignored.
        """
        for algorithm in SUPPORTED_DIGEST_ALGORITHMS:
            s = SecretLinkSerializer(algorithm_name=algorithm)
            st = TimedSecretLinkSerializer(algorithm_name=algorithm)

            for serializer in (s, st):
                # serializer.validate_token() already handles BadData
                data = serializer.validate_token(
                    token, expected_data=expected_data, force=force
                )

                if data:
                    return data
