# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-License-Identifier: MIT

"""Tests utils."""

import flask_security
from invenio_accounts.testutils import login_user_via_session


def login_user(client, user):
    """Log user in."""
    flask_security.login_user(user)
    login_user_via_session(client, email=user.email)


def logout_user(client):
    """Log current user out."""
    flask_security.logout_user()

    with client.session_transaction() as session:
        if "user_id" in session:
            del session["user_id"]
            del session["_user_id"]
