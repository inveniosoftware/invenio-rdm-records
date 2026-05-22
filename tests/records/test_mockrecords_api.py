# SPDX-FileCopyrightText: 2021-2026 CERN.
# SPDX-License-Identifier: MIT

"""Data layer tests for record/community integration."""

import pytest
from invenio_communities.communities.records.api import Community
from invenio_communities.errors import SetDefaultCommunityError
from jsonschema import ValidationError
from sqlalchemy.exc import IntegrityError

from tests.records.mock_module.api import MockRecord


@pytest.fixture()
def c(app, db, location):
    """A community fixture."""
    _c = Community.create({})
    db.session.commit()
    return Community.get_record(_c.id)


@pytest.fixture()
def c2(app, db, location):
    """Another community fixture."""
    _c = Community.create({})
    db.session.commit()
    return Community.get_record(_c.id)


@pytest.fixture()
def record(app, db, c):
    """A community fixture."""
    r = MockRecord.create({})
    r.communities.add(c, default=True)
    r.commit()
    db.session.commit()
    return r


def test_record_create_empty(app, db):
    """Smoke test."""
    record = MockRecord.create({})
    db.session.commit()
    assert record.schema

    # JSONSchema validation works.
    pytest.raises(ValidationError, MockRecord.create, {"metadata": {"title": 1}})


def test_get(db, record, c):
    """Loading a record should load communties and default."""
    r = MockRecord.get_record(record.id)
    assert c in r.communities
    assert r.communities.default == c


def test_add(db, c):
    """Test adding a record to a community."""
    # With default
    record = MockRecord.create({})
    record.communities.add(c, default=True)
    assert record.communities.default == c
    record.commit()
    assert record["communities"] == {
        "default": str(c.id),
        "ids": [str(c.id)],
    }
    db.session.commit()

    # No default
    record = MockRecord.create({})
    record.communities.add(c)
    assert record.communities.default is None
    record.commit()
    assert record["communities"] == {"ids": [str(c.id)]}
    db.session.commit()


def test_add_existing(db, c):
    """Test addding same community twice."""
    record = MockRecord.create({})
    record.communities.add(c)
    record.communities.add(c)
    # Adding a community already added, will raise integrity error.
    pytest.raises(IntegrityError, record.commit)
    # Rollback to avoid error in pytest-invenio "location" fixture.
    db.session.rollback()


def test_len_contains(record, c, c2):
    assert len(record.communities) == 1
    assert c in record.communities
    assert str(c.id) in record.communities
    assert c2 not in record.communities
    assert str(c2.id) not in record.communities


def test_remove(db, c, record):
    """Test removal of community."""
    record.communities.remove(c)
    assert len(record.communities) == 0
    record.commit()
    assert record["communities"] == {}
    db.session.commit()

    # Removing non-existing raises an error
    pytest.raises(ValueError, record.communities.remove, c2)


def test_iter(db, record, c):
    # With cache hit
    assert list(record.communities) == [c]
    # Without cache hit
    record = MockRecord.get_record(record.id)
    assert list(record.communities) == [c]


def test_ids(db, record, c):
    assert list(record.communities.ids) == [str(c.id)]


def test_change_default(db, record, c, c2):
    assert record.communities.default == c
    del record.communities.default
    assert record.communities.default is None

    with pytest.raises(SetDefaultCommunityError):
        # record not part of c2, so will fail
        record.communities.default = c2

    record.communities.add(c2)
    record.communities.default = c2
    assert record.communities.default == c2


def test_clear(db, record):
    assert len(record.communities) == 1
    record.communities.clear()
    assert len(record.communities) == 0
    record.commit()
    assert record["communities"] == {}


def test_refresh(db, record, c2):
    assert len(record.communities) == 1
    # Mess up internals
    record.communities._communities_ids = set()
    record.communities._default_id = str(c2.id)
    record.commit()
    db.session.commit()
    # Still messed up
    record = MockRecord.get_record(record.id)
    assert len(record.communities) == 0
    # Refresh to fix
    record.communities.refresh()
    assert len(record.communities) == 1
