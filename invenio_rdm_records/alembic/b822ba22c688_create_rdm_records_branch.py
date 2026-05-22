# SPDX-FileCopyrightText: 2021 TU Wien.
# SPDX-License-Identifier: MIT

"""Create RDM-Records branch."""

# revision identifiers, used by Alembic.
revision = "b822ba22c688"
down_revision = None
branch_labels = ("invenio_rdm_records",)
depends_on = "dbdbc1b19cf2"


def upgrade():
    """Upgrade database."""
    pass


def downgrade():
    """Downgrade database."""
    pass
