#
# This file is part of Invenio.
# Copyright (C) 2023-2024 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Add indexes."""

from alembic import op

# revision identifiers, used by Alembic.
revision = "ff9bec971d30"
down_revision = "faf0cefa79a0"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_index(
        op.f("ix_rdm_drafts_metadata_bucket_id"),
        "rdm_drafts_metadata",
        ["bucket_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_rdm_drafts_metadata_media_bucket_id"),
        "rdm_drafts_metadata",
        ["media_bucket_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_rdm_records_metadata_bucket_id"),
        "rdm_records_metadata",
        ["bucket_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_rdm_records_metadata_media_bucket_id"),
        "rdm_records_metadata",
        ["media_bucket_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_rdm_records_metadata_version_bucket_id"),
        "rdm_records_metadata_version",
        ["bucket_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_rdm_records_metadata_version_media_bucket_id"),
        "rdm_records_metadata_version",
        ["media_bucket_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_rdm_drafts_files_object_version_id"),
        "rdm_drafts_files",
        ["object_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_rdm_drafts_media_files_object_version_id"),
        "rdm_drafts_media_files",
        ["object_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_rdm_records_files_object_version_id"),
        "rdm_records_files",
        ["object_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_rdm_records_files_version_object_version_id"),
        "rdm_records_files_version",
        ["object_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_rdm_records_media_files_object_version_id"),
        "rdm_records_media_files",
        ["object_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_rdm_records_media_files_version_object_version_id"),
        "rdm_records_media_files_version",
        ["object_version_id"],
        unique=False,
    )


def downgrade():
    """Downgrade database."""
    op.drop_index(
        op.f("ix_rdm_records_metadata_version_media_bucket_id"),
        table_name="rdm_records_metadata_version",
    )
    op.drop_index(
        op.f("ix_rdm_records_metadata_version_bucket_id"),
        table_name="rdm_records_metadata_version",
    )
    op.drop_index(
        op.f("ix_rdm_records_metadata_media_bucket_id"),
        table_name="rdm_records_metadata",
    )
    op.drop_index(
        op.f("ix_rdm_records_metadata_bucket_id"), table_name="rdm_records_metadata"
    )
    op.drop_index(
        op.f("ix_rdm_drafts_metadata_media_bucket_id"), table_name="rdm_drafts_metadata"
    )
    op.drop_index(
        op.f("ix_rdm_drafts_metadata_bucket_id"), table_name="rdm_drafts_metadata"
    )
    op.drop_index(
        op.f("ix_rdm_drafts_files_object_version_id"), table_name="rdm_drafts_files"
    )
    op.drop_index(
        op.f("ix_rdm_drafts_media_files_object_version_id"),
        table_name="rdm_drafts_media_files",
    )
    op.drop_index(
        op.f("ix_rdm_records_files_object_version_id"), table_name="rdm_records_files"
    )
    op.drop_index(
        op.f("ix_rdm_records_files_version_object_version_id"),
        table_name="rdm_records_files_version",
    )
    op.drop_index(
        op.f("ix_rdm_records_media_files_version_object_version_id"),
        table_name="rdm_records_media_files_version",
    )
    op.drop_index(
        op.f("ix_rdm_records_media_files_object_version_id"),
        table_name="rdm_records_media_files",
    )
