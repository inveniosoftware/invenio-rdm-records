# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Add parent_id index."""

from alembic import op

# revision identifiers, used by Alembic.
revision = "c2d3e4f5a6b7"
down_revision = "1780576627"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_index(
        op.f("ix_rdm_records_metadata_parent_id"),
        "rdm_records_metadata",
        ["parent_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_rdm_drafts_metadata_parent_id"),
        "rdm_drafts_metadata",
        ["parent_id"],
        unique=False,
    )


def downgrade():
    """Downgrade database."""
    op.drop_index(
        op.f("ix_rdm_records_metadata_parent_id"),
        table_name="rdm_records_metadata",
    )

    op.drop_index(
        op.f("ix_rdm_drafts_metadata_parent_id"),
        table_name="rdm_drafts_metadata",
    )
