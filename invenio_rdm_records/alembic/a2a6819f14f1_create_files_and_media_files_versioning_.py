#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create files and media files versioning table."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql, postgresql
from sqlalchemy_utils import JSONType, UUIDType

# revision identifiers, used by Alembic.
revision = "a2a6819f14f1"
down_revision = "2186256e8d9b"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    # create version table for record files
    op.create_table(
        "rdm_records_files_version",
        sa.Column(
            "created",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column("id", UUIDType(), nullable=False),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column(
            "key",
            sa.Text().with_variant(mysql.VARCHAR(length=255), "mysql"),
            nullable=False,
        ),
        sa.Column("record_id", UUIDType(), nullable=False),
        sa.Column("object_version_id", UUIDType(), nullable=True),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "id", "transaction_id", name=op.f("pk_rdm_records_files_version")
        ),
    )
    op.create_index(
        "ix_rdm_records_files_version_end_transaction_id",
        "rdm_records_files_version",
        ["end_transaction_id"],
        unique=False,
    )
    op.create_index(
        "ix_rdm_records_files_version_operation_type",
        "rdm_records_files_version",
        ["operation_type"],
        unique=False,
    )
    op.create_index(
        "ix_rdm_records_files_version_transaction_id",
        "rdm_records_files_version",
        ["transaction_id"],
        unique=False,
    )

    # create version table for record media files
    op.create_table(
        "rdm_records_media_files_version",
        sa.Column(
            "created",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column("id", UUIDType(), nullable=False),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column(
            "key",
            sa.Text().with_variant(mysql.VARCHAR(length=255), "mysql"),
            nullable=False,
        ),
        sa.Column("record_id", UUIDType(), nullable=False),
        sa.Column("object_version_id", UUIDType(), nullable=True),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "id", "transaction_id", name=op.f("pk_rdm_records_media_files_version")
        ),
    )
    op.create_index(
        "ix_rdm_records_media_files_version_end_transaction_id",
        "rdm_records_media_files_version",
        ["end_transaction_id"],
        unique=False,
    )
    op.create_index(
        "ix_rdm_records_media_files_version_operation_type",
        "rdm_records_media_files_version",
        ["operation_type"],
        unique=False,
    )
    op.create_index(
        "ix_rdm_records_media_files_version_transaction_id",
        "rdm_records_media_files_version",
        ["transaction_id"],
        unique=False,
    )


def downgrade():
    """Downgrade database."""
    # drop files version table and indices
    op.drop_index(
        "ix_rdm_records_files_version_end_transaction_id",
        table_name="rdm_records_files_version",
    )
    op.drop_index(
        "ix_rdm_records_files_version_operation_type",
        table_name="rdm_records_files_version",
    )
    op.drop_index(
        "ix_rdm_records_files_version_transaction_id",
        table_name="rdm_records_files_version",
    )
    op.drop_table("rdm_records_files_version")

    # drop media files version table and indices
    op.drop_index(
        "ix_rdm_records_media_files_version_end_transaction_id",
        table_name="rdm_records_media_files_version",
    )
    op.drop_index(
        "ix_rdm_records_media_files_version_operation_type",
        table_name="rdm_records_media_files_version",
    )
    op.drop_index(
        "ix_rdm_records_media_files_version_transaction_id",
        table_name="rdm_records_media_files_version",
    )
    op.drop_table("rdm_records_media_files_version")
