# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
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

from .requests.access.permissions import AccessRequestTokenNeed
from .secret_links import LinkNeed, SecretLink
from .tokens import RATNeed, validate_rat
from .tokens.errors import RATFeatureDisabledError


def get_or_create_user(email):
    """Get or create a user."""
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
            if getattr(o, name):
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
    token = request.args.get("token", session.get("token", None))

    session["token"] = token
    if token:
        try:
            data = SecretLink.load_token(token)
            if data:
                identity.provides.add(LinkNeed(data["id"]))
        except SignatureExpired:
            flash(_("Your shared link has expired."))

    resource_access_token = request.args.get(
        current_app.config.get("RDM_RESOURCE_ACCESS_TOKEN_REQUEST_ARG", None), None
    )
    if resource_access_token:
        if not current_app.config.get("RDM_RESOURCE_ACCESS_TOKENS_ENABLED", False):
            raise RATFeatureDisabledError()

        rat_signer, payload = validate_rat(resource_access_token)
        identity.provides.add(
            RATNeed(
                rat_signer, payload["record_id"], payload["file"], payload["access"]
            )
        )

    access_request_token = request.args.get(
        "access_request_token", session.get("access_request_token", None)
    )
    session["access_request_token"] = access_request_token
    if access_request_token:
        identity.provides.add(AccessRequestTokenNeed(access_request_token))
