#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create table for secret links."""

import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op

# revision identifiers, used by Alembic.
revision = "0cf260eb8e97"
down_revision = "4a15e8671f4d"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_table(
        "rdm_records_secret_links",
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("token", sa.Text, nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("permission_level", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rdm_records_secret_links")),
    )
    op.create_index(
        op.f("ix_rdm_records_secret_links_created"),
        "rdm_records_secret_links",
        ["created"],
        unique=False,
    )


def downgrade():
    """Downgrade database."""
    op.drop_index(
        op.f("ix_rdm_records_secret_links_created"),
        table_name="rdm_records_secret_links",
    )
    op.drop_table("rdm_records_secret_links")
