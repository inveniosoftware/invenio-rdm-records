# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utility functions."""

from flask_security.confirmable import confirm_user
from flask_security.utils import hash_password
from invenio_accounts.proxies import current_datastore
from invenio_db import db
from invenio_users_resources.services.users.tasks import reindex_user


def get_or_create_user(email):
    """Get or create a user."""
    user = current_datastore.get_user(email)
    if not user:
        user = current_datastore.create_user(
            email=email,
            username=email.split("@")[0],
            password=hash_password("123456"),
            active=True,
            preferences=dict(visibility="public", email_visibility="public"),
        )
        confirm_user(user)
        db.session.commit()
        reindex_user(user.id)
    return user
