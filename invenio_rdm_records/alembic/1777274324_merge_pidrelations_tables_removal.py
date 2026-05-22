# SPDX-FileCopyrightText: 2016-2018 CERN.
# SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
# SPDX-License-Identifier: MIT

"""Merge PIDRelations tables removal to single head."""

# revision identifiers, used by Alembic.
revision = "1777274324"
down_revision = ("912251a56a49", "a3957490361d")
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""


def downgrade():
    """Downgrade database."""
