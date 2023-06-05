# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test SecretLink model class."""

from datetime import datetime, timedelta

from invenio_db import db

from invenio_rdm_records.secret_links.models import SecretLink


def test_secret_link_creation(app):
    """Check SecretLink.create()."""
    with app.app_context():
        link = SecretLink.create("preview")
        db.session.commit()

        assert link.permission_level == "preview"
        assert not link.extra_data
        assert not link.is_expired

        # check that the token's ID points to its SecretLink
        assert SecretLink.load_token(link.token)["id"] == str(link.id)


def test_secret_link_not_expired(app):
    """Check is_expired for a link that will expire in 10 minutes."""
    with app.app_context():
        in_10_mins = datetime.utcnow() + timedelta(minutes=10)
        link = SecretLink.create("view", expires_at=in_10_mins)
        db.session.commit()

        assert not link.is_expired


def test_secret_link_expired(app):
    """Check is_expired for a link that expired 10 minutes ago."""
    with app.app_context():
        _10_mins_ago = datetime.utcnow() - timedelta(minutes=10)
        link = SecretLink.create("view", expires_at=_10_mins_ago)
        db.session.commit()

        assert link.is_expired


def test_secret_link_revoke(app):
    """Ensure that revoke() deletes secret links."""
    with app.app_context():
        link = SecretLink.create("view")
        db.session.commit()
        uuid = link.id

        assert SecretLink.query.get(uuid) == link
        link.revoke()
        db.session.commit()

        assert SecretLink.query.get(uuid) is None


def test_secret_link_get_by_token(app):
    """Check get_by_token for a valid token."""
    with app.app_context():
        link = SecretLink.create("view")
        db.session.commit()

        link2 = SecretLink.get_by_token(link.token)

        assert link == link2


def test_secret_link_get_by_invalid_token(app):
    """Check get_by_token for an invalid token."""
    with app.app_context():
        link = SecretLink.get_by_token("asdf")

        assert link is None


def test_secret_link_get_by_old_token(app):
    """Ensure that deleted/revoked links aren't returned by get_by_token."""
    with app.app_context():
        link = SecretLink.create("view")
        db.session.commit()

        token = link.token
        link.revoke()
        db.session.commit()

        link = SecretLink.get_by_token(token)

        assert link is None


def test_secret_link_validate_token(app):
    """Check validate_token for a valid token."""
    with app.app_context():
        in_10_mins = datetime.utcnow() + timedelta(minutes=10)
        link = SecretLink.create("view", expires_at=in_10_mins)
        db.session.commit()

        assert link.validate_token(link.token, expected_data={})


def test_secret_link_validate_token_expired(app):
    """Check validate_token for an expired token."""
    with app.app_context():
        _10_mins_ago = datetime.utcnow() - timedelta(minutes=10)
        link = SecretLink.create("view", expires_at=_10_mins_ago)
        db.session.commit()

        assert not link.validate_token(link.token, expected_data={})
