# SPDX-FileCopyrightText: 2025 TU Wien.
# SPDX-License-Identifier: MIT

"""Drop ``RDMRecordQuota.user_id`` unique constraint."""

from alembic import op

# revision identifiers, used by Alembic.
revision = "1746626978"
down_revision = "ff9bec971d30"
branch_labels = ()
depends_on = [
    # invenio_collections/alembic/425b691f768b_create_collections_tables.py
    "425b691f768b"
]


def upgrade():
    """Upgrade database."""
    op.drop_constraint(
        "uq_rdm_records_quota_user_id", "rdm_records_quota", type_="unique"
    )


def downgrade():
    """Downgrade database."""
    op.create_unique_constraint(
        "uq_rdm_records_quota_user_id", "rdm_records_quota", ["user_id"]
    )
