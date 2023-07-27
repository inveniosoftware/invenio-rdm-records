#
# This file is part of Invenio.
# Copyright (C) 2023 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Add deletion status to RDMRecords."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2186256e8d9b"
down_revision = "ff860d48fb4b"
branch_labels = ()
depends_on = None


def _get_default_deletion_status():
    """Try to get the default value for record deletion status."""
    try:
        # first try: get the default value from the DB model class
        from invenio_rdm_records.records.models import RDMRecordMetadata

        default_value = RDMRecordMetadata.deletion_status.default.arg
        assert len(default_value) == 1

    except Exception:
        try:
            # second try: try to get the value from the enum (more flaky)
            from invenio_rdm_records.records.systemfields.deletion_status import (
                RecordDeletionStatusEnum,
            )

            default_value = RecordDeletionStatusEnum.PUBLISHED.value
            assert len(default_value) == 1

        except Exception:
            # fallback: just use 'P', as that's the current default (most flaky)
            default_value = "P"

    return default_value


def upgrade():
    """Upgrade database."""
    # step 1: create the columns, but make them nullable for now
    op.add_column(
        "rdm_records_metadata",
        sa.Column("deletion_status", sa.String(length=1), nullable=True),
    )
    op.add_column(
        "rdm_records_metadata_version",
        sa.Column(
            "deletion_status",
            sa.String(length=1),
            nullable=True,
        ),
    )

    # step 2: set default values for existing rows
    default_value = _get_default_deletion_status()
    metadata_table = sa.sql.table(
        "rdm_records_metadata", sa.sql.column("deletion_status")
    )
    metadata_version_table = sa.sql.table(
        "rdm_records_metadata_version", sa.sql.column("deletion_status")
    )
    op.execute(metadata_table.update().values(deletion_status=default_value))
    op.execute(metadata_version_table.update().values(deletion_status=default_value))

    # step 3: make the original table not nullable
    op.alter_column("rdm_records_metadata", "deletion_status", nullable=False)


def downgrade():
    """Downgrade database."""
    op.drop_column("rdm_records_metadata_version", "deletion_status")
    op.drop_column("rdm_records_metadata", "deletion_status")
