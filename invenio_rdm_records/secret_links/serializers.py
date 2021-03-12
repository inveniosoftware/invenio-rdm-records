# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Secret links for sharing access to records."""

import secrets
from datetime import datetime

from flask import current_app
from itsdangerous import BadData, JSONWebSignatureSerializer, Serializer, \
    SignatureExpired, TimedJSONWebSignatureSerializer


class TokenSerializerMixin(Serializer):
    """Mix-in class for token serializers.

    The tokens store a reference to some object (e.g. SecretLinks) via an ID,
    and they can hold additional data.
    Through the addition of a random value in the token, it is (almost)
    ensured that any two generated tokens are different, even when generated
    with otherwise identical data.
    """

    def create_token(self, obj_id, extra_data=dict()):
        """Create a token referencing the object id with extra data.

        Note: random data is added to ensure that no two tokens are identical.
        """
        token = self.dumps(
            {
                "id": str(obj_id),
                "data": extra_data,
                "random": secrets.token_hex(16),
            }
        )

        if isinstance(token, bytes):
            # normalize the token to always be a string
            token = token.decode("utf8")

        return token

    def validate_token(self, token, expected_data=None, force=False):
        """Load and validate secret link token.

        :param token: Token value.
        :param expected_data: A dictionary of key/values that must be present
                              in the data part of the token (i.e. included
                              via ``extra_data`` in ``create_token``).
        :param force: Load token data even if signature expired.
                      Default: False.
        """
        try:
            # Load token and remove random data.
            data = self.load_token(token, force=force)

            # Compare expected data with data in token.
            expected_data = expected_data or {}
            for k, v in expected_data.items():
                if data["data"].get(k) != v:
                    return None

            return data

        except BadData:
            return None

    def load_token(self, token, force=False):
        """Load data in a token.

        :param token: Token to load.
        :param force: Load token data even if signature expired.
                      Default: False.
        """
        try:
            data = self.loads(token)

        except SignatureExpired as e:
            if not force:
                raise

            data = e.payload

        del data["random"]
        return data


class TimedSecretLinkSerializer(
    TimedJSONWebSignatureSerializer, TokenSerializerMixin
):
    """Serializer for expiring secret links."""

    def __init__(self, expires_at=None, **kwargs):
        """Initialize underlying TimedJSONWebSignatureSerializer.

        If ``expires_at`` is set to ``None``, a default value will
        be used by the ``TimedJSONWebSignatureSerializer`` superclass.
        """
        assert isinstance(expires_at, datetime) or expires_at is None

        dt = (expires_at - datetime.utcnow()) if expires_at else None

        super().__init__(
            current_app.config["SECRET_KEY"],
            expires_in=int(dt.total_seconds()) if dt else None,
            salt="rdm-records-timed-link",
            **kwargs
        )


class SecretLinkSerializer(JSONWebSignatureSerializer, TokenSerializerMixin):
    """Serializer for secret links."""

    def __init__(self, **kwargs):
        """Initialize underlying JSONWebSignatureSerializer."""
        super().__init__(
            current_app.config["SECRET_KEY"], salt="rdm-records-link", **kwargs
        )
