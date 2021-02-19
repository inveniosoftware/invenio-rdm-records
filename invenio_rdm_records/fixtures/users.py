# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Users fixtures module."""

import secrets
import string

import yaml
from flask import current_app
from flask_security.utils import hash_password
from invenio_access.models import ActionUsers
from invenio_access.proxies import current_access
from invenio_accounts.proxies import current_datastore
from invenio_db import db


class UsersFixture:
    """Users fixture."""

    def __init__(self, search_path, filename):
        """Initialize the fixture."""
        self._search_path = search_path
        self._filename = filename

    def load(self):
        """Load the fixture."""
        with open(self._search_path.path(self._filename)) as fp:
            data = yaml.load(fp)
            for email, user_data in data.items():
                self.create_user(email, user_data)

    def create_user(self, email, entry):
        """Load a single user."""
        # when the user's password is set in the configuration, then
        # this overrides everything else
        password = current_app.config.get(
            "RDM_RECORDS_USER_FIXTURE_PASSWORDS", {}
        ).get(email)

        if not password:
            # for auto-generated passwords use letters, digits,
            # and some punctuation marks
            alphabet = string.ascii_letters + string.digits + "+,-_."
            gen_passwd = "".join(secrets.choice(alphabet) for i in range(20))
            password = entry.get("password") or gen_passwd

        user_data = {
            "email": email,
            "active": entry.get("active", False),
            "password": hash_password(password),
        }
        user = current_datastore.create_user(**user_data)

        for role in entry.get("roles", []):
            current_datastore.add_role_to_user(user, role)

        for action in entry.get("allow", []):
            action = current_access.actions[action]
            db.session.add(ActionUsers.allow(action, user_id=user.id))

        db.session.commit()
