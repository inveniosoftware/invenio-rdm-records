#
# This file is part of Invenio.
# Copyright (C) 2023 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create access request tokens table."""

import sqlalchemy as sa
import sqlalchemy_utils as utils
from alembic import op

# revision identifiers, used by Alembic.
revision = "cfcb8cb78708"
down_revision = "a6bfa06b1a6d"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_table(
        "rdm_records_access_request_tokens",
        sa.Column("id", utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("token", sa.String(512), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("record_pid", sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint(
            "id", name=op.f("pk_rdm_records_access_request_tokens")
        ),
    )
    op.create_index(
        op.f("ix_rdm_records_access_request_tokens_created"),
        "rdm_records_access_request_tokens",
        ["created"],
        unique=False,
    )


def downgrade():
    """Downgrade database."""
    op.drop_index(
        op.f("ix_rdm_records_access_request_tokens_created"),
        table_name="rdm_records_access_request_tokens",
    )
    op.drop_table("rdm_records_access_request_tokens")
