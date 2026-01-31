# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resource access tokens API."""

from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app
from invenio_db import db
from invenio_oauth2server.models import Token
from marshmallow import Schema, fields

from .errors import (
    ExpiredTokenError,
    InvalidTokenError,
    InvalidTokenIDError,
    MissingTokenIDError,
    TokenDecodeError,
)
from .scopes import tokens_generate_scope


class SubjectSchema(Schema):
    """Resource access token JWT subject schema."""

    pid_value = fields.Str(data_key="record_id", required=True)
    file_key = fields.Str(data_key="file", load_default=None)
    permission = fields.Str(data_key="access", load_default=None)


def validate_rat(token):
    """Decodes a JWT token's payload and signer and performs validation."""
    # Retrieve token ID from "kid"
    try:
        headers = jwt.get_unverified_header(token)
        access_token_id = headers.get("kid")
    except jwt.DecodeError:
        raise TokenDecodeError()
    except jwt.InvalidTokenError:
        raise InvalidTokenError()

    if not access_token_id:
        raise MissingTokenIDError()
    if not access_token_id.isdigit():
        raise InvalidTokenIDError()

    access_token = db.session.get(Token, int(access_token_id))
    is_invalid_scope = (
        access_token and tokens_generate_scope.id not in access_token.scopes
    )

    if not access_token or is_invalid_scope:
        raise InvalidTokenError()
    try:
        payload = jwt.decode(
            token,
            key=access_token.access_token,
            algorithms=current_app.config.get(
                "RDM_RESOURCE_ACCESS_TOKENS_WHITELISTED_JWT_ALGORITHMS",
                ["HS256", "HS384", "HS512"],
            ),
            options={
                # Based on the JWT spec (https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.2)
                # the "sub" claim has to be a string. However, we are not enforcing this
                # and are assuming that the "sub" claim is an object/dictionary.
                # PyJWT v2.10.0 started enforcing this and we are disabling this check.
                "verify_sub": False,
                "require": ["iat", "sub"],
            },
        )

        if not isinstance(payload.get("sub"), dict):
            raise InvalidTokenError()

        token_lifetime = current_app.config.get(
            "RDM_RESOURCE_ACCESS_TOKENS_JWT_LIFETIME", timedelta(minutes=30)
        )
        # Verify that the token is not expired based on its issue time
        issued_at = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        if (issued_at + token_lifetime) < datetime.now(timezone.utc):
            raise ExpiredTokenError()

    except jwt.DecodeError:
        raise TokenDecodeError()
    except jwt.InvalidTokenError:
        raise InvalidTokenError()

    return access_token.user.id, payload["sub"]
