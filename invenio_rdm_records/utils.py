# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utility functions."""

from collections import ChainMap

from flask import current_app, flash, request, session
from flask_security.confirmable import confirm_user
from flask_security.utils import hash_password
from invenio_accounts.proxies import current_datastore
from invenio_db import db
from invenio_i18n import _
from invenio_users_resources.services.users.tasks import reindex_users
from itsdangerous import SignatureExpired
from marshmallow import ValidationError

from .requests.access.permissions import AccessRequestTokenNeed
from .secret_links import LinkNeed, SecretLink
from .tokens import RATNeed, validate_rat
from .tokens.errors import (
    InvalidTokenSubjectError,
    RATFeatureDisabledError,
    TokenDecodeError,
)


def get_or_create_user(email):
    """Get or create a user."""
    with db.session.no_autoflush:
        user = current_datastore.get_user(email)
    if not user:
        user = current_datastore.create_user(
            email=email,
            username=email.split("@")[0],
            password=hash_password("123456"),
            active=True,
            preferences=dict(
                visibility="public",
                email_visibility="public",
                locale=current_app.config.get("BABEL_DEFAULT_LOCALE", "en"),
                timezone=current_app.config.get(
                    "BABEL_DEFAULT_TIMEZONE", "Europe/Zurich"
                ),
            ),
        )
        confirm_user(user)
        db.session.commit()
        reindex_users([user.id])
    return user


class ChainObject:
    """Read-only wrapper to chain attribute/key lookup over multiple objects."""

    def __init__(self, *objs, aliases=None):
        """Constructor."""
        self._objs = objs
        self._aliases = aliases or {}

    def __getattr__(self, name):
        """Lookup attribute over all objects."""
        # Check aliases first
        aliases = super().__getattribute__("_aliases")
        if name in aliases:
            return aliases[name]

        objs = super().__getattribute__("_objs")
        for o in objs:
            if getattr(o, name, None):
                return getattr(o, name)
        raise AttributeError()

    def __getitem__(self, key):
        """Index lookup over all objects."""
        objs = super().__getattribute__("_objs")
        return ChainMap(*objs)[key]

    def get(self, key, default=None):
        """Index lookup a la ``dict.get`` over all objects."""
        objs = super().__getattribute__("_objs")
        return ChainMap(*objs).get(key, default=default)


def verify_token(identity):
    """Verify the token and provide identity with corresponding need."""
    secret_link_token_arg = "token"
    token = None
    token_source = None
    has_secret_link_token = False
    arg_token = request.args.get(secret_link_token_arg, None)
    session_token = session.get(secret_link_token_arg, None)
    if arg_token:
        token = arg_token
        token_source = "arg"
    elif session_token:
        token = session_token
        token_source = "session"

    if token:
        try:
            data = SecretLink.load_token(token)
            if data:
                identity.provides.add(LinkNeed(data["id"]))
                # In order for anonymous users with secret link to perform vulnerable HTTP requests
                # ("POST", "PUT", "PATCH", "DELETE"), CSRF token must be set
                request.csrf_cookie_needs_reset = True
            session[secret_link_token_arg] = token
            has_secret_link_token = True
        except SignatureExpired:
            # It the token came from "args", we notify that the link has expired
            if token_source == "arg":
                flash(_("Your shared link has expired."))
            # We remove the token from the session to avoid flashing the message
            session.pop(secret_link_token_arg, None)

    # NOTE: This logic is getting very complex becuase of possible arg naming conflicts
    # for the Zenodo use-case. It can be simplified once the conflict changes
    rat_enabled = current_app.config.get("RDM_RESOURCE_ACCESS_TOKENS_ENABLED", False)
    rat_arg = current_app.config.get("RDM_RESOURCE_ACCESS_TOKEN_REQUEST_ARG", None)
    # we can have a "naming conflict" if both secret links and RATs use the same arg key
    rat_arg_name_conflict = rat_arg == secret_link_token_arg
    rat = request.args.get(rat_arg, None)
    if rat and not (rat_arg_name_conflict and has_secret_link_token):
        if not rat_enabled:
            raise RATFeatureDisabledError()

        try:
            rat_signer, payload = validate_rat(rat)
            schema_cls = current_app.config.get(
                "RDM_RESOURCE_ACCESS_TOKENS_SUBJECT_SCHEMA"
            )
            if schema_cls:
                try:
                    rat_need_data = schema_cls().load(payload)
                except ValidationError:
                    raise InvalidTokenSubjectError()
            else:
                rat_need_data = payload
            identity.provides.add(RATNeed(rat_signer, **rat_need_data))
        except TokenDecodeError:
            pass

    access_request_token = request.args.get(
        "access_request_token", session.get("access_request_token", None)
    )
    if access_request_token:
        session["access_request_token"] = access_request_token
        identity.provides.add(AccessRequestTokenNeed(access_request_token))
