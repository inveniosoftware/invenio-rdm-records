#
# This file is part of Invenio.
# Copyright (C) 2023 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Add origin and description to secret links."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a6bfa06b1a6d"
down_revision = "9e0ac518b9df"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.add_column(
        "rdm_records_secret_links",
        sa.Column("origin", sa.String(255), nullable=False, server_default=""),
    )
    op.add_column(
        "rdm_records_secret_links",
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
    )


def downgrade():
    """Downgrade database."""
    op.drop_column("rdm_records_secret_links", "description")
    op.drop_column("rdm_records_secret_links", "origin")
