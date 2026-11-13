# SPDX-FileCopyrightText: 2026 California Institute of Technology.
# SPDX-License-Identifier: MIT

"""Add max_additional_quota_size to rdm_users_quota."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1794592987"
down_revision = "1780576627"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.add_column(
        "rdm_users_quota",
        sa.Column("max_additional_quota_size", sa.BigInteger(), nullable=True),
    )


def downgrade():
    """Downgrade database."""
    op.drop_column("rdm_users_quota", "max_additional_quota_size")
