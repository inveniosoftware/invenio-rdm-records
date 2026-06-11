# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2024 Graz University of Technology.
# Copyright (C) 2026 CESNET z.s.p.o.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test alembic recipes for Invenio-RDM-Records."""

import pytest
from invenio_db.utils import alembic_test_context, drop_alembic_version_table

# Expected tables created by tests.records.mock_module (no alembic recipes).
_MOCK_MODULE_MIGRATIONS = {
    ("add_table", "mock_metadata"),
    ("add_table", "mock_community"),
    ("add_index", "ix_mock_community_record_id"),
}


def _assert_no_unexpected_migrations(alembic):
    """Assert Alembic metadata diff only contains known mock-module tables."""
    for migration in alembic.compare_metadata():
        if (migration[0], migration[1].name) not in _MOCK_MODULE_MIGRATIONS:
            raise RuntimeError(f"Unexpected migration: {migration}")


def test_alembic(base_app, database):
    """Test alembic recipes."""
    db = database
    ext = base_app.extensions["invenio-db"]

    if db.engine.name == "sqlite":
        raise pytest.skip("Upgrades are not supported on SQLite.")

    base_app.config["ALEMBIC_CONTEXT"] = alembic_test_context()

    # Check that this package's SQLAlchemy models have been properly registered
    tables = [x for x in db.metadata.tables]
    assert "rdm_drafts_files" in tables
    assert "rdm_drafts_metadata" in tables
    assert "rdm_records_files" in tables
    assert "rdm_records_files_version" in tables
    assert "rdm_records_metadata_version" in tables
    assert "rdm_records_metadata" in tables
    assert "rdm_parents_metadata" in tables
    assert "rdm_parents_community" in tables
    assert "rdm_versions_state" in tables
    assert "rdm_drafts_media_files" in tables
    assert "rdm_records_media_files" in tables
    assert "rdm_records_media_files_version" in tables

    # Check that Alembic agrees that there's no further tables to create.
    assert not ext.alembic.compare_metadata()

    # Drop everything and recreate tables all with Alembic
    db.drop_all()
    drop_alembic_version_table()
    ext.alembic.upgrade()
    _assert_no_unexpected_migrations(ext.alembic)

    # Try to upgrade and downgrade
    ext.alembic.stamp()
    ext.alembic.downgrade(target="96e796392533")
    ext.alembic.upgrade()
    _assert_no_unexpected_migrations(ext.alembic)

    drop_alembic_version_table()
