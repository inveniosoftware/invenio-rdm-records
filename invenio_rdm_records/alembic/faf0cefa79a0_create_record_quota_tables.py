#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create record and user quota tables."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy_utils.types import UUIDType

# revision identifiers, used by Alembic.
revision = "faf0cefa79a0"
down_revision = "ffd725001655"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_table(
        "rdm_records_quota",
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.Column("id", UUIDType(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("quota_size", sa.BigInteger(), nullable=False),
        sa.Column("max_file_size", sa.BigInteger(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("parent_id", UUIDType(), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["rdm_parents_metadata.id"],
            name=op.f("fk_rdm_records_quota_parent_id_rdm_parents_metadata"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rdm_records_quota")),
        sa.UniqueConstraint("parent_id", name=op.f("uq_rdm_records_quota_parent_id")),
        sa.UniqueConstraint("user_id", name=op.f("uq_rdm_records_quota_user_id")),
    )
    op.create_table(
        "rdm_users_quota",
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.Column("id", UUIDType(), nullable=False),
        sa.Column("quota_size", sa.BigInteger(), nullable=False),
        sa.Column("max_file_size", sa.BigInteger(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["accounts_user.id"],
            name=op.f("fk_rdm_users_quota_user_id_accounts_user"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rdm_users_quota")),
        sa.UniqueConstraint("user_id", name=op.f("uq_rdm_users_quota_user_id")),
    )


def downgrade():
    """Downgrade database."""
    op.drop_table("rdm_records_quota")
    op.drop_table("rdm_users_quota")
